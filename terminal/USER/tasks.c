//tasks.c

#include "tasks.h"


//camera task
#define jpeg_buf_size 10*1024
volatile u32 jpeg_data_len = 0;
volatile u8 jpeg_data_rdy = 0;
u32* jpeg_buf;

u8 cam_on = 0;
u8 dht_on = 0;


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

void camera_init(void)
{
	while(OV2640_Init())
	{
		printf("OV2640 Err! Retrying...\r\n");
		delay_ms(500);
	}
	
	My_DCMI_Init();
	DCMI_DMA_Init((u32)jpeg_buf, 0, jpeg_buf_size, DMA_MemoryDataSize_Word, DMA_MemoryInc_Enable);
	OV2640_JPEG_Mode();
	OV2640_OutSize_Set(320, 240); //QVGA MODE_DECRYPT
	
	DCMI_Start();
}

void dht11_read(void)
{
	u8 temperature = 0, humidity = 0;
	char* data = mymalloc(SRAMIN, 16);
	
	DCMI_Stop();
	
	while(DHT11_Read_Data(&temperature, &humidity))
	{
		printf("DHT11 Read Failed, Retrying...\r\n");
		delay_ms(500);
	}
	
	sprintf(data, "%d %d\r\n", temperature, humidity);
	
	u8* p = (u8*)data;
	int ret = write(sock, p, strlen(data));
	if(ret > 0)
		printf("Socket Sent %s\r\n", p);
	
	myfree(SRAMIN, data);
	camera_init();
	
	delay_us(2000 * 1000);
}


#define CAM_TASK_PRIO 14
#define CAM_STK_SIZE 256
OS_STK CAM_TASK_STK[CAM_STK_SIZE];

void camera_task(void *pdata)
{
	jpeg_buf = mymalloc(SRAMIN, jpeg_buf_size);
	
	while(socket_rdy == 0)
		delay_ms(100);
	
	camera_init();
	
	while(1)
	{
		if(cam_on && jpeg_data_rdy == 1)
		{
			printf("Cam Captured %d bits\r\n", jpeg_data_len * 4);
			jpeg_data_rdy = 3;
			delay_ms(10);
			
			if(dht_on)
			{
				dht11_read();
				dht_on = 0;
			}
		}
		delay_ms(2000);
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
		if(key == KEY0_PRES)
		{
			cam_on = !cam_on;
			if(cam_on)
				printf("Camera On\r\n");
			else
				printf("Camera Off\r\n");
		}
		else if(key == KEY1_PRES)
		{
			dht_on = 1;
			printf("DHT11 Read\r\n");
		}
		OSTimeDlyHMSM(0,0,0,10);
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
		OSTimeDlyHMSM(0,0,0,500);
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
	OSTaskCreate(led_task,(void*)0, (OS_STK*)&LED_TASK_STK[LED_STK_SIZE - 1], LED_TASK_PRIO);
	OSTaskCreate(key_task,(void*)0, (OS_STK*)&KEY_TASK_STK[KEY_STK_SIZE - 1], KEY_TASK_PRIO);
	
	OSTaskSuspend(OS_PRIO_SELF);
	printf("Tasks created!\r\n");
	
	OS_EXIT_CRITICAL();
}
