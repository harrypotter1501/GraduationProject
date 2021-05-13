//apps.h

#ifndef __APPS_H
#define __APPS_H


#include "sys.h"
#include "delay.h"

#include "lwip/api.h"
#include "includes.h"

#include "malloc.h"
#include "key.h"

#include "sockets.h"
#include <string.h>


typedef struct http_get_resp
{
	u16 code;
	char* data;
} HTTPResp;


#define DEVICE_ID "testsys"
#define DEVICE_KEY "abcdef"

#define SERVER_IP "192.168.0.103"
#define SERVER_PORT_TCP 8080
#define SERVER_PORT_SO 8088//6000//

#define RX_BUFSIZE 150
#define TX_BUFSIZE 100

#define TCP_RECV_TIMEOUT 100
#define SO_CONN_TIMEOUT 100
#define SO_RECV_TIMEOUT 100


extern int sock;
extern u8 socket_rdy;

INT8U apps_init(void);
u8 verify_device(void);


#endif /* __APPS_H */
