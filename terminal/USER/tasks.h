//tasks.h

#ifndef __TASKS_H
#define __TASKS_H


#include "sys.h"
#include "delay.h"
#include "usart.h"

#include "led.h"
#include "key.h"
#include "lwip_comm.h"
#include "LAN8720.h"
#include "malloc.h"
#include "ov2640.h"
#include "dcmi.h"
#include "dht11.h"

#include "lwip_comm.h"
#include "includes.h"
#include "lwipopts.h"

#include "apps.h"


#define SEND_NUM 1
//#define JPEG_BATCH


void start_task(void *pdata);


#endif /* __TASKS_H */
