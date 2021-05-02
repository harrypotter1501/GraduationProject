//tasks.c

#include "tasks.h"


//camera task
#define jpeg_buf_size 5*1024
u32* jpeg_buf;
volatile u32 jpeg_data_len = 0;
volatile u8 jpeg_data_rdy = 0;

u32* send_buf;
u32 send_buf_idx = 0;

u8 cam_on = 0;
u8 dht_on = 0;
u8 frame = 1;

u16 ov_out_mode[5][2] = {
	0, 0,       //default
	320,240,	//QVGA
	640,480,	//VGA
	800,600,	//SVGA
	1024,768,	//XGA
};


void jpeg_data_process(void)
{
	if(jpeg_data_rdy==0)
	{
		DMA_Cmd(DMA2_Stream1, DISABLE);
		while (DMA_GetCmdStatus(DMA2_Stream1) != DISABLE){}
		jpeg_data_len=jpeg_buf_size-DMA_GetCurrDataCounter(DMA2_Stream1);
		jpeg_data_rdy=1;
	}
	if(jpeg_data_rdy==2)
	{
		DMA2_Stream1->NDTR=jpeg_buf_size;	
		DMA_SetCurrDataCounter(DMA2_Stream1,jpeg_buf_size);
		DMA_Cmd(DMA2_Stream1, ENABLE);
		jpeg_data_rdy=0;
	}
}


#define CAM_TASK_PRIO 14
#define CAM_STK_SIZE 256
OS_STK CAM_TASK_STK[CAM_STK_SIZE];

void camera_task(void *pdata)
{
	jpeg_buf = mymalloc(SRAMIN, jpeg_buf_size * 4);
	send_buf = mymalloc(SRAMEX, jpeg_buf_size * 4 * SEND_NUM);
	
	if(jpeg_buf == 0x00 || send_buf == 0x00)
	{
		printf("Malloc Failed!\r\n");
		while(1);
	}
	
	OV2640_JPEG_Mode();
	My_DCMI_Init();
	DCMI_DMA_Init((u32)jpeg_buf, jpeg_buf_size, DMA_MemoryDataSize_Word, DMA_MemoryInc_Enable);
	OV2640_OutSize_Set(1024, 768); //QVGA MODE_DECRYPT
	
	DCMI_Start();
	
	while(socket_rdy == 0)
		delay_ms(100);
	
	u16 tval = 1000;
	
	while(1)
	{
		if(cam_on && jpeg_data_rdy == 1)
		{
			//cam_on = 0;
			//mymemcpy(send_buf + send_buf_idx, jpeg_buf, jpeg_data_len);
			//printf("Camera Captured %d bytes\r\n", jpeg_data_len * 4);
			u8* p = (u8*)jpeg_buf;
			send_buf_idx += jpeg_data_len;
			
#ifdef JPEG_BATCH
			
			static u8 send_buf_cnt = 0;
			send_buf_cnt++;
			
			if(send_buf_cnt == SEND_NUM)
				send_buf_cnt = 0;
			else
			{
				jpeg_data_rdy = 2;
				continue;
			}
			
			p = (u8*)send_buf;
			
#endif /* JPEG_BATCH */
			
			int ret = write(sock, p, send_buf_idx * 4);
			if(ret <= 0)
				printf("Socket Error: No data sent\r\n");
			
			send_buf_idx = 0;
			jpeg_data_rdy = 2;
		}
		tval = (u16)1000/frame;
		delay_ms(tval);
	}
}

char* dht_data_buf;
u8 dht_data_rdy = 0;

#define DHT_TASK_PRIO 15
#define DHT_STK_SIZE 128
OS_STK DHT_TASK_STK[DHT_STK_SIZE];

void dht11_task(void *pdata)
{
	u8 temperature = 0, humidity = 0;
	dht_data_buf = mymalloc(SRAMIN, 16);
	
	while(1)
	{
		if(dht_on == 1)
		{
			dht_on = 0;
			
			u8 cnt = 0;
			while(DHT11_Read_Data(&temperature, &humidity))
			{
				cnt++;
				if(cnt > 10)
				{
					printf("DHT11 Read Failed\r\n");
					break;
				}
				delay_ms(500);
			}
			
			sprintf(dht_data_buf, "%d %d\r\n", temperature, humidity);
			int ret = write(sock, dht_data_buf, strlen(dht_data_buf));
			if(ret <= 0)
				printf("Socket Error: No data sent\r\n");
		}
		delay_ms(1000);
	}
}


//key task
#define KEY_TASK_PRIO 		18
#define KEY_STK_SIZE		128
OS_STK KEY_TASK_STK[KEY_STK_SIZE];

void key_task(void *pdata)
{
	u8 key; 
	while(1)
	{
		key = KEY_Scan(0);
		switch(key)
		{
			case KEY0_PRES:
			{
				switch(++cam_on)
				{
					case 1:
					{
						printf("QVGA Mode\r\n");
						break;
					}
					case 2:
					{
						printf("VGA Mode\r\n");
						break;
					}
					case 3:
					{
						printf("SVGA Mode\r\n");
						break;
					}
					case 4:
					{
						printf("XGA Mode\r\n");
						break;
					}
					default:
					{
						printf("Camera off\r\n");
						cam_on = 0;
						break;
					}
				}
			}
			case KEY1_PRES:
			{
				if(frame > 1)
					frame--;
				printf("Frame: %d/s\r\n", frame);
				break;
			}
			case KEY2_PRES:
			{
				dht_on = 1;
				printf("DHT11 Read\r\n");
				break;
			}
			case WKUP_PRES:
			{
				frame++;
				printf("Frame: %d/s\r\n", frame);
				break;
			}
			default:
				break;
		}
		delay_ms(100);
	}
}


//led task
#define LED_TASK_PRIO		19
#define LED_STK_SIZE		64
OS_STK	LED_TASK_STK[LED_STK_SIZE];

void led_task(void *pdata)
{
	while(1)
	{
		LED0 = !LED0;
		delay_ms(500);
 	}
}


//start task
void start_task(void *pdata)
{
	OS_CPU_SR cpu_sr;
	pdata = pdata;
	
	OSStatInit();
	OS_ENTER_CRITICAL();
	
#if LWIP_DHCP
	lwip_comm_dhcp_creat();
#endif
	
	OSTaskCreate(camera_task,(void*)0, (OS_STK*)&CAM_TASK_STK[CAM_STK_SIZE - 1], CAM_TASK_PRIO);
	OSTaskCreate(dht11_task,(void*)0, (OS_STK*)&DHT_TASK_STK[DHT_STK_SIZE - 1], DHT_TASK_PRIO);
	OSTaskCreate(led_task,(void*)0, (OS_STK*)&LED_TASK_STK[LED_STK_SIZE - 1], LED_TASK_PRIO);
	OSTaskCreate(key_task,(void*)0, (OS_STK*)&KEY_TASK_STK[KEY_STK_SIZE - 1], KEY_TASK_PRIO);
	
	OSTaskSuspend(OS_PRIO_SELF);
	printf("Tasks created!\r\n");
	
	OS_EXIT_CRITICAL();
}
