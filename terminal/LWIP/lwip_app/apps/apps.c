//apps.c

#include "apps.h"


//global args
struct netconn* tcp_conn;
char* NET_RX_BUF;
char* HTTP_RX_BUF;
char* HTTP_TX_BUF;

int sock;

OS_EVENT* sem_http_rdy;
OS_EVENT* sem_req;
OS_EVENT* sem_resp;


//recieve task
extern u8 cam_on;
extern u8 dht_on;
extern u8 frame;

#define RECV_TASK_PRIO 10
#define RECV_STK_SIZE 128
OS_STK RECV_TASK_STK[RECV_STK_SIZE];

void socket_recv_task(void *args)
{
	LWIP_UNUSED_ARG(args);
	OSTaskSuspend(OS_PRIO_SELF);
	
	while(1)
	{
		int ret = read(sock, NET_RX_BUF, RX_BUFSIZE);
		if(ret > 0)
		{
			printf("Socket Recieved %d bytes:\r\n%s\r\n", ret, NET_RX_BUF);
			u8 cmd = NET_RX_BUF[0];
			dht_on = cmd & 0x01;
			cam_on = (cmd & 0x02) >> 1;
			if(cam_on)
				cam_on = ((cmd & 0x0C) >> 2) + 1;
			
			u8 frame_n = (cmd & 0x30) >> 4;
			switch(frame_n)
			{
				case 0:
				{
					frame = 1;
					break;
				}
				case 1:
				{
					frame = 3;
					break;
				}
				case 2:
				{
					frame = 6;
					break;
				}
				default:
					frame = 1;
			}
		}
		delay_ms(1000);
	}
}


////send task
//extern u32* send_buf;
//extern u32 send_buf_idx;
//extern u8 jpeg_data_rdy;

//extern char* dht_data_buf;
//extern u8 dht_data_rdy;


//#define SEND_TASK_PRIO 11
//#define SEND_STK_SIZE 128
//OS_STK SEND_TASK_STK[SEND_STK_SIZE];

//void socket_send_task(void *args)
//{
//	LWIP_UNUSED_ARG(args);
//	
//	int ret;
//	
//	while(1)
//	{
////		if(jpeg_data_rdy == 3)
////		{
////			for(u8 i = 0; i < 100; i++)
////				printf("%d ", send_buf[i]);
////			//u8* p = (u8*)send_buf;
////			ret = write(sock, send_buf, send_buf_idx * 4);
////			printf("\r\n");
////			if(ret <= 0)
////				printf("Socket Error: No data sent\r\n");
////			send_buf_idx = 0;
////			jpeg_data_rdy = 2;
////		}
//		
//		
//		
//		delay_ms(10);
//	}
//}


//sockets
u8 socket_rdy = 0;

void socket_connect(void)
{
	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));
	addr.sin_len = sizeof(addr);
	addr.sin_family = AF_INET;
	addr.sin_port = htons(SERVER_PORT_SO);
	addr.sin_addr.s_addr = inet_addr(SERVER_IP);
	
	sock = socket(AF_INET, SOCK_STREAM, 0);
	LWIP_ASSERT("Socket not created!", sock >= 0);
	
	u8 timeout = SO_CONN_TIMEOUT;
	setsockopt(sock, SOL_SOCKET, SO_CONTIMEO, &timeout, sizeof(u8));
	
	while(1)
	{
		int ret = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
		if(ret == ERR_OK)
			break;
		else
		{
			closesocket(sock);
			printf("Socket Connect Failed with Code %d\r\n", ret);
		}
		delay_ms(5000);
	}
	
	timeout = SO_RECV_TIMEOUT;
	setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(u8));
	printf("Socket Connected!\r\n");
	
	OSTaskResume(RECV_TASK_PRIO);
	socket_rdy = 1;
}


//tcp netconn
ip_addr_t resolve_ip(const char* ip)
{
	ip_addr_t ip_addr;
	int n1, n2, n3, n4;
	
	sscanf(ip, "%d.%d.%d.%d", &n1, &n2, &n3, &n4);
	IP4_ADDR(&ip_addr, (u8)n1, (u8)n2, (u8)n3, (u8)n4);
	
	return ip_addr;
}

err_t fetch_rx_data(struct netconn* tcp_conn, char* rx_buf)
{
	OS_CPU_SR cpu_sr;
	
	struct netbuf* recv_buf;
	err_t err = netconn_recv(tcp_conn, &recv_buf);
	if(err == ERR_OK)
	{
		OS_ENTER_CRITICAL();
		memset(rx_buf, 0, RX_BUFSIZE);
		u32 data_len = 0;
		for(struct pbuf* q=recv_buf->p; q != NULL; q = q->next)
		{
			if(q->len > (RX_BUFSIZE - data_len))
				memcpy(rx_buf + data_len, q->payload, (RX_BUFSIZE - data_len));
			else
				memcpy(rx_buf + data_len, q->payload, q->len);
			
			data_len += q->len;  	
			if(data_len > RX_BUFSIZE)
				break;
		}
		
		if(data_len < RX_BUFSIZE)
			HTTP_RX_BUF[data_len] = '\0';
		else
			HTTP_RX_BUF[RX_BUFSIZE - 1] = '\0';
		
		OS_EXIT_CRITICAL();
		netbuf_delete(recv_buf);
		return ERR_OK;
	}
	else
		return err;
}


//http get task
#define GET_TASK_PRIO 12
#define GET_STK_SIZE 128
OS_STK GET_TASK_STK[GET_STK_SIZE];

void http_get_task(void* args)
{
	LWIP_UNUSED_ARG(args);
	
	ip_addr_t ip_addr = resolve_ip(SERVER_IP);
	
	while(1)
	{
		tcp_conn = netconn_new(NETCONN_TCP);
		netconn_set_recvtimeout(tcp_conn, TCP_RECV_TIMEOUT);
		
		u16_t port = SERVER_PORT_TCP;
		err_t err = netconn_connect(tcp_conn, &ip_addr, port);
		
		if(err != ERR_OK)
		{
			netconn_delete(tcp_conn);
			printf("Connection Failed with Code %d\r\n", err);
		}
		else
		{
			OSSemPost(sem_http_rdy);
			tcp_conn->recv_timeout = 100;
			
			while(1)
			{
				INT8U err_sem;
				OSSemPend(sem_req, 0, &err_sem);
				
				u8 len = strlen(HTTP_TX_BUF);
				
				err = netconn_write(tcp_conn, HTTP_TX_BUF, len, NETCONN_COPY);
				if(err != ERR_OK)
					printf("Netconn Write Failed!\r\n");
				else
				{
					printf("Netconn Sent: %d bits\r\n", len);
					sprintf(HTTP_TX_BUF, "");
					u8 timeout = TCP_RECV_TIMEOUT;
					
					while(timeout > 0)
					{
						err = fetch_rx_data(tcp_conn, HTTP_RX_BUF);
						if(err == ERR_OK)
						{
							netconn_close(tcp_conn);
							netconn_delete(tcp_conn);
							
							OSSemPost(sem_resp);
							break;
						}
						else if(err == ERR_TIMEOUT)
							--timeout;
						else
						{
							printf("Recieve Failed with Code: %d\r\n", err);
							break;
						}
						delay_ms(100);
					}
					
					if(timeout <= 0)
						printf("HTTP Response Timeout!\r\n");
				}
			}
		}
		delay_ms(1000);
	}
}


//verify device
u8 validate_response(void)
{
	u8 len = strlen(HTTP_RX_BUF);
	if(len < 6)
		return 1;
	else
		return strcmp(HTTP_RX_BUF + (len - 4), "\r\nOK");
}

u8 verify_device(void)
{
	OSSemPost(sem_req);
	
	INT8U err;
	OSSemPend(sem_resp, 1000, &err);
	
	if(validate_response())
		return 1;
	else
	{
		printf("Device Verifed!\r\n");
		sprintf(HTTP_RX_BUF, "");
		return 0;
	}
}


//apps main task
#define MAIN_TASK_PRIO 13
#define MAIN_STK_SIZE 128
OS_STK MAIN_TASK_STK[MAIN_STK_SIZE];

void app_main_task(void* args)
{
	LWIP_UNUSED_ARG(args);
	
	NET_RX_BUF = mymalloc(SRAMIN, RX_BUFSIZE);
	HTTP_RX_BUF = mymalloc(SRAMIN, RX_BUFSIZE);
	HTTP_TX_BUF = mymalloc(SRAMIN, TX_BUFSIZE);
	
	sprintf(HTTP_TX_BUF, "GET /device/?device_id=%s&device_key=%s HTTP/1.1\r\n"
						 "Host: http://%s:%d\r\n"
						 "\r\n\r\n", DEVICE_ID, DEVICE_KEY, SERVER_IP, SERVER_PORT_TCP);
	
//	INT8U err;
//	OSSemPend(sem_http_rdy, 0, &err);
//	
//	while(verify_device())
//	{
//		printf("Verify Device Failed! Retrying...\r\n");
//		delay_ms(1000);
//		break;
//	}
	delay_ms(3000);
	
	socket_connect();
	
	while(1)
	{
		//do something
		delay_ms(1000);
	}
}


//task create
INT8U apps_init(void)
{
	OS_CPU_SR cpu_sr;
	
	sem_http_rdy = OSSemCreate(0);
	sem_req = OSSemCreate(0);
	sem_resp = OSSemCreate(0);
	
	INT8U res = 0;
	OS_ENTER_CRITICAL();
	
	res |= OSTaskCreate(socket_recv_task, (void*)0, (OS_STK*)&RECV_TASK_STK[RECV_STK_SIZE - 1], RECV_TASK_PRIO);
	//res |= OSTaskCreate(socket_send_task, (void*)0, (OS_STK*)&SEND_TASK_STK[SEND_STK_SIZE - 1], SEND_TASK_PRIO);
	//res |= OSTaskCreate(http_get_task, (void*)0,  (OS_STK*)&GET_TASK_STK[GET_STK_SIZE - 1], GET_TASK_PRIO);
	res |= OSTaskCreate(app_main_task, (void*)0, (OS_STK*)&MAIN_TASK_STK[MAIN_STK_SIZE - 1], MAIN_TASK_PRIO);

	OS_EXIT_CRITICAL();
	return res;
}
