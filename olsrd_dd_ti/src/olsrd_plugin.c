/*
 * The olsr.org Optimized Link-State Routing daemon(olsrd)
 * Copyright (c) 2004, Andreas T�nnesen(andreto@olsr.org)
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions 
 * are met:
 *
 * * Redistributions of source code must retain the above copyright 
 *   notice, this list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright 
 *   notice, this list of conditions and the following disclaimer in 
 *   the documentation and/or other materials provided with the 
 *   distribution.
 * * Neither the name of olsr.org, olsrd nor the names of its 
 *   contributors may be used to endorse or promote products derived 
 *   from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * Visit http://www.olsr.org for more information.
 *
 * If you find this software useful feel free to make a donation
 * to the project. For more information see the website or contact
 * the copyright holders.
 *
 * $Id: olsrd_plugin.c,v 1.12 2005/06/02 15:09:37 br1 Exp $
 */

/*
 * Dynamic linked library for the olsr.org olsr daemon
 */


#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/in.h>

#include "olsrd_plugin.h"
#include "olsrd_dot_draw.h"


#define PLUGIN_NAME    "OLSRD toplogy information plugin - based on dot draw 0.3"
#define PLUGIN_VERSION "0.02"
#define PLUGIN_AUTHOR   ""
#define MOD_DESC PLUGIN_NAME " " PLUGIN_VERSION
#define PLUGIN_INTERFACE_VERSION 4


struct in_addr ipc_accept_ip;
int ipc_port;


static void __attribute__ ((constructor)) 
my_init(void);

static void __attribute__ ((destructor)) 
my_fini(void);


/**
 *Constructor
 */
static void
my_init()
{
  /* Print plugin info to stdout */
  printf("%s\n", MOD_DESC);

  /* defaults for parameters */
  ipc_port = 2006;
  ipc_accept_ip.s_addr = htonl(INADDR_LOOPBACK);
}


/**
 *Destructor
 */
static void
my_fini()
{
  /* Calls the destruction function
   * olsr_plugin_exit()
   * This function should be present in your
   * sourcefile and all data destruction
   * should happen there - NOT HERE!
   */
  olsr_plugin_exit();
}


int 
olsrd_plugin_interface_version()
{
  return PLUGIN_INTERFACE_VERSION;
}


int
olsrd_plugin_register_param(char *key, char *value)
{
  if(!strcmp(key, "port"))
    {
     ipc_port = atoi(value);
     printf("(DOT DRAW) listening on port: %d\n", ipc_port);
    }

  if(!strcmp(key, "accept"))
    {
	inet_aton(value, &ipc_accept_ip);
	printf("(DOT DRAW) accept only: %s\n", inet_ntoa(ipc_accept_ip));
    }
  return 1;
}
