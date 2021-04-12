//main.c

#include "main.h"


//start task
#define START_TASK_PRIO		20
#define START_STK_SIZE		64
OS_STK START_TASK_STK[START_STK_SIZE];
void start_task(void *pdata);


extern void camera_task(void* pdata);

//main
int main(void)
{
	delay_init(168);
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
	uart_init(115200);
	LED_Init();
	KEY_Init();
	
	while(DHT11_Init())
	{
		printf("DHT11 Error, Retrying...\r\n");
		delay_ms(500);
	}
	
	FSMC_SRAM_Init();
	mymem_init(SRAMIN);
	mymem_init(SRAMEX);
	mymem_init(SRAMCCM);
	
	while(OV2640_Init())
	{
		printf("OV2640 Err! Retrying...\r\n");
		delay_ms(500);
	}
	
	printf("Hardware Init Success!\r\n");
	delay_ms(100);
	
	OSInit();
	printf("UCOS Init Success!\r\n");
	
	while(lwip_comm_init())
	{
		printf("Lwip Init failed! Retrying...\r\n");
		delay_ms(100);
	}
	printf("Lwip Init Success!\r\n");
	
	while(apps_init())
	{
		printf("Apps Init Failed! Retrying...\r\n");
		delay_ms(100);
	}
	printf("Apps Init Success!\r\n");
	delay_ms(100);
	
	OSTaskCreate(start_task,(void*)0,(OS_STK*)&START_TASK_STK[START_STK_SIZE-1],START_TASK_PRIO);
	OSStart();
}

