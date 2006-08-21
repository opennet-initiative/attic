/*
Copyright 2006 Sebastian Hagen
 This file is part of nlct_.

 nlct_ is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License version 2 
 as published by the Free Software Foundation

 nlct_ is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with alfredi; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/
#include <Python.h>
#include <fcntl.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

struct nfct_mask {
   int mask;
   char *name;
};

static PyObject *NfnlError;
static PyObject *ct_event_retval = NULL;
int ct_event_pyexc = 0;


static PyObject *ct_dump_conntrack_table(struct nfct_handle *nch, int family) {
   int srv;
   static PyObject *retval;
   
   retval = PyList_New(0);
   if (!retval) return NULL;
   ct_event_retval = retval;
   ct_event_pyexc = 0;
   
   /* at least this one doesn't directly check our uid */
   srv = nfct_dump_conntrack_table(nch, family);
    
   ct_event_retval = NULL;
   
   if (srv == 0) {
      return retval;
   } else {
      Py_DECREF(retval);
      if (!ct_event_pyexc)
         PyErr_SetString(NfnlError, strerror(abs(srv))); /* not a py error in the callback handler */
      return NULL;
   }
}


static PyObject *ct_event_conntrack(struct nfct_handle *nch) {
   int srv;
   static PyObject *retval;
   
   retval = PyList_New(0);
   if (!retval) return NULL;
   ct_event_retval = retval;
   ct_event_pyexc = 0;
   /* probably a mistake; this really shouldn't depend on uid == 0 */
   srv = nfct_event_conntrack(nch);
   
   ct_event_retval = NULL;
   
   if (srv == 0)
      return retval;
   else {
      Py_DECREF(retval);
      if (!ct_event_pyexc)
         PyErr_SetString(NfnlError, strerror(abs(srv))); /* not a py error in the callback handler */
      return NULL;
   }
}

inline static PyObject *ct_nfcfct_to_py_address(union nfct_address *t, int proto) {
   return ((proto == AF_INET) ? 
      PyLong_FromUnsignedLong((long) ntohl(t->v4)) :
      Py_BuildValue("NNNN",
         PyLong_FromUnsignedLong((long) ntohl(t->v6[0])),
         PyLong_FromUnsignedLong((long) ntohl(t->v6[1])),
         PyLong_FromUnsignedLong((long) ntohl(t->v6[2])),
         PyLong_FromUnsignedLong((long) ntohl(t->v6[3]))
      )
   );
}

inline static PyObject *ct_nfcfct_to_py_l4(union nfct_l4 *a, unsigned char proto) {
   if (proto == IPPROTO_TCP) return PyInt_FromLong((long) a->tcp.port);
   if (proto == IPPROTO_UDP) return PyInt_FromLong((long) a->udp.port);
   if (proto == IPPROTO_ICMP) return Py_BuildValue("NNN",
      PyInt_FromLong((long) a->icmp.type),
      PyInt_FromLong((long) a->icmp.code),
      PyInt_FromLong((long) a->icmp.id)
   );
   if (proto == IPPROTO_SCTP) return PyInt_FromLong((long) a->sctp.port);
   return PyInt_FromLong((long) a->all);
}

inline static PyObject *ct_nfcfct_to_py_tuple(struct nfct_tuple *t) {
   return Py_BuildValue("NNNNNN",
      ct_nfcfct_to_py_address(&t->src, t->l3protonum),
      ct_nfcfct_to_py_address(&t->dst, t->l3protonum),
      PyInt_FromLong((long) t->l3protonum),
      PyInt_FromLong((long) t->protonum),
      ct_nfcfct_to_py_l4(&t->l4src, t->l3protonum),
      ct_nfcfct_to_py_l4(&t->l4dst, t->l3protonum)
   );
}

inline static PyObject *ct_nfcfct_to_py_protoinfo(union nfct_protoinfo *p, unsigned char proto) {
   return ((proto == IPPROTO_TCP) ? PyInt_FromLong((long) p->tcp.state) : (Py_INCREF(Py_None), Py_None));
}

inline static PyObject *ct_nfctct_to_py_counters(struct nfct_counters *c) {
   return Py_BuildValue("NN", PyLong_FromUnsignedLongLong(c->packets), PyLong_FromUnsignedLongLong(c->bytes));
}

inline static PyObject *ct_nfctct_to_py_nat(struct nfct_nat *n, unsigned char proto1, unsigned char proto2) {
   return Py_BuildValue("NNNN",
      PyLong_FromUnsignedLong(n->min_ip),
      PyLong_FromUnsignedLong(n->max_ip),
      ct_nfcfct_to_py_l4(&n->l4min, proto1),
      ct_nfcfct_to_py_l4(&n->l4max, proto2)
   );
}

inline static PyObject *ct_nfctct_to_py(struct nfct_conntrack *ct, int type, unsigned int flags) {
   static PyObject *rv; 
   rv = Py_BuildValue("iNNssssssssN",
      type,
      ct_nfcfct_to_py_tuple(&ct->tuple[NFCT_DIR_ORIGINAL]),
      ct_nfcfct_to_py_tuple(&ct->tuple[NFCT_DIR_REPLY]),
      NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
      ct_nfctct_to_py_nat(&ct->nat, ct->tuple[NFCT_DIR_ORIGINAL].l3protonum, ct->tuple[NFCT_DIR_REPLY].l3protonum)
   );
   
   if (flags & NFCT_TIMEOUT) PyTuple_SetItem(rv, 3, PyLong_FromUnsignedLong(ct->timeout));
   if (flags & NFCT_MARK) PyTuple_SetItem(rv, 4, PyLong_FromUnsignedLong(ct->mark));
   if (flags & NFCT_STATUS) PyTuple_SetItem(rv, 5, PyLong_FromUnsignedLong(ct->status));
   if (flags & NFCT_USE) PyTuple_SetItem(rv, 6, PyLong_FromUnsignedLong(ct->use));
   if (flags & NFCT_ID) PyTuple_SetItem(rv, 7, PyLong_FromUnsignedLong(ct->id));
   if (flags & NFCT_PROTOINFO) PyTuple_SetItem(rv, 8, ct_nfcfct_to_py_protoinfo(&ct->protoinfo, ct->tuple[NFCT_DIR_ORIGINAL].l3protonum));
   if (flags & NFCT_COUNTERS_ORIG) PyTuple_SetItem(rv, 9, ct_nfctct_to_py_counters(&ct->counters[NFCT_DIR_ORIGINAL]));
   if (flags & NFCT_COUNTERS_RPLY) PyTuple_SetItem(rv, 10, ct_nfctct_to_py_counters(&ct->counters[NFCT_DIR_REPLY]));
   return rv;
}

int ct_callback(void *ct, unsigned int flags, int type, void *data) {
   int *pyexc = data;
   static PyObject *nelem;
   
   nelem = ct_nfctct_to_py(ct, type, flags);
   
   if (!nelem || PyList_Append(ct_event_retval, nelem)) {
      *pyexc = 1;
      return -1; /* abort iteration */
   } else
      return 0;
}

typedef struct {
   PyObject_HEAD
   struct nfct_handle *nch;
} NfctHandle;

static void NfctHandle_dealloc(NfctHandle *self) {
   if (self->nch) nfct_close(self->nch);
   self->ob_type->tp_free((PyObject*) self);
}

static int NfctHandle_init(NfctHandle *self, PyObject *args, PyObject *kwargs) {
   static char *kwlist[] = {NULL};
   int srv;
   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "", kwlist)) return -1; 
   
   if (self->nch && (srv = nfct_close(self->nch))) {
      PyErr_SetString(NfnlError, strerror(abs(srv)));
      return -1;
   }
   
   self->nch = nfct_open(CONNTRACK, NFCT_ALL_CT_GROUPS);
   if (!self->nch) {
      PyErr_SetString(NfnlError, strerror(errno));
      return -1;
   }
   
   if (fcntl(nfct_fd(self->nch), F_SETFL, O_NONBLOCK)) {
      PyErr_SetString(NfnlError, strerror(errno));
      nfct_close(self->nch);
      return -1;
   };
   
   nfct_register_callback(self->nch, ct_callback, &ct_event_pyexc);
   return 0;
}

static PyObject *NfctHandle_dump_conntrack_table(NfctHandle *self, PyObject *args, PyObject *kwargs) {
   int family;
   static char *kwlist[] = {"family", NULL};
   if (!self->nch) {
      PyErr_SetString(NfnlError, "NfctHandle instance hasn't been initialized");
      return NULL;
   }
   
   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i", kwlist, &family)) {
      Py_DECREF(args);
      return NULL;
   }
   
   return ct_dump_conntrack_table(self->nch, family);
}

static PyObject *NfctHandle_event_conntrack(NfctHandle *self) {
   if (!self->nch) {
      PyErr_SetString(NfnlError, "NfctHandle instance hasn't been initialized");
      return NULL;
   }
   return ct_event_conntrack(self->nch);
}

static PyObject *NfctHandle_fileno(NfctHandle *self) {
   if (!self->nch) {
      PyErr_SetString(NfnlError, "NfctHandle instance hasn't been initialized");
      return NULL;
   }
   return PyInt_FromLong(nfct_fd(self->nch));
}

static PyObject *NfctHandle_close(NfctHandle *self) {
   if (self->nch) {
      if (nfct_close(self->nch)) {
         PyErr_SetString(NfnlError, strerror(errno));
         return NULL;
      };
      self->nch = NULL;
   }
   Py_INCREF(Py_None);
   return Py_None;
}

PyDoc_STRVAR(NfctHandle_doc,
"NfctHandle() -> NfctHandle object\n\n\
Open an NfctHandle. This requires elevated privileges.");

PyDoc_STRVAR(NfctHandle_dump_conntrack_table_doc, 
"dump_conntrack_table(family) -> sequence\n\n\
Return conntrack table for specified address family (see socket.AF_*), and\n\
return recevied data; this will probably also return any other data buffered\n\
on this nfct handle since it was last read. This operation requires\n\
CAP_NET_ADMIN.");

PyDoc_STRVAR(NfctHandle_event_conntrack_doc,
"event_conntrack() -> sequence\n\n\
Return all conntrack events currently buffered on this nfct handle (and flush\n\
that buffer). This doesn't require any special privileges per se, but some\n\
versions of libnetlink_conntrack contain a misfeature preventing use of the\n\
wrapped ct_event_conntrack() for uids != 0.");

PyDoc_STRVAR(NfctHandle_fileno_doc,
"fileno() -> integer\n\n\
Return fd for the netlink socket used internally by this nfct handle. The fd\n\
will only change on __init__(), and can be used to manipulate the socket\n\
directly or to wait on it with select() or poll().");

PyDoc_STRVAR(NfctHandle_close_doc,
"close()\n\n\
Close nfct handle; the instance will behave unitializedly after this call.");

static PyMethodDef NfctHandle_methods[] = {
   {"dump_conntrack_table", (PyCFunction)NfctHandle_dump_conntrack_table, METH_VARARGS, NfctHandle_dump_conntrack_table_doc},
   {"event_conntrack", (PyCFunction)NfctHandle_event_conntrack, METH_NOARGS, NfctHandle_event_conntrack_doc},
   {"fileno", (PyCFunction)NfctHandle_fileno, METH_NOARGS, NfctHandle_fileno_doc},
   {"close", (PyCFunction)NfctHandle_close, METH_NOARGS, NfctHandle_close_doc},
   {NULL}  /* Sentinel */
};

static PyTypeObject NfctHandleType = {
   PyObject_HEAD_INIT(NULL)
   0,                         /*ob_size*/
   "nfct_.NfctHandle",        /*tp_name*/
   sizeof(NfctHandle),        /*tp_basicsize*/
   0,                         /*tp_itemsize*/
   (destructor)NfctHandle_dealloc, /*tp_dealloc*/
   0,                         /*tp_print*/
   0,                         /*tp_getattr*/
   0,                         /*tp_setattr*/
   0,                         /*tp_compare*/
   0,                         /*tp_repr*/
   0,                         /*tp_as_number*/
   0,                         /*tp_as_sequence*/
   0,                         /*tp_as_mapping*/
   0,                         /*tp_hash */
   0,                         /*tp_call*/
   0,                         /*tp_str*/
   0,                         /*tp_getattro*/
   0,                         /*tp_setattro*/
   0,                         /*tp_as_buffer*/
   Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,             /*tp_flags*/
   NfctHandle_doc,            /* tp_doc */
   0,                         /* tp_traverse */
   0,                         /* tp_clear */
   0,                         /* tp_richcompare */
   0,                         /* tp_weaklistoffset */
   0,                         /* tp_iter */
   0,                         /* tp_iternext */
   NfctHandle_methods,        /* tp_methods */
   0,                         /* tp_members */
   0,                         /* tp_getset */
   0,                         /* tp_base */
   0,                         /* tp_dict */
   0,                         /* tp_descr_get */
   0,                         /* tp_descr_set */
   0,                         /* tp_dictoffset */
   (initproc)NfctHandle_init, /* tp_init */
   0,                         /* tp_alloc */
   0,                         /* tp_new */
};

static PyMethodDef pynlct__methods[] = {
   {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
initnlct_(void) {
   int i;
   PyObject *module;
   struct nfct_mask nfct_masks[] = {
      /* see libnetfilter_conntrack.h for the meanings of these */
      /* nfct flag masks 
      {NFCT_STATUS, "NFCT_STATUS"},
      {NFCT_PROTOINFO, "NFCT_PROTOINFO"},
      {NFCT_TIMEOUT, "NFCT_TIMEOUT"},
      {NFCT_MARK, "NFCT_MARK"},
      {NFCT_COUNTERS_ORIG, "NFCT_COUNTERS_ORIG"},
      {NFCT_COUNTERS_RPLY, "NFCT_COUNTERS_RPLY"},
      {NFCT_USE, "NFCT_USE"},
      {NFCT_ID, "NFCT_ID"},*/
      /* nfct type possibilities */
      {NFCT_MSG_UNKNOWN, "NFCT_MSG_UNKNOWN"},
      {NFCT_MSG_NEW, "NFCT_MSG_NEW"},
      {NFCT_MSG_UPDATE, "NFCT_MSG_UPDATE"},
      {NFCT_MSG_DESTROY, "NFCT_MSG_DESTROY"},
      /* nfct status masks */
      {IPS_EXPECTED, "IPS_EXPECTED"},
      {IPS_SEEN_REPLY, "IPS_SEEN_REPLY"},
      {IPS_ASSURED, "IPS_ASSURED"},
      {IPS_CONFIRMED, "IPS_CONFIRMED"},
      {IPS_SRC_NAT, "IPS_SRC_NAT"},
      {IPS_DST_NAT, "IPS_DST_NAT"},
      {IPS_NAT_MASK, "IPS_NAT_MASK"},
      {IPS_SEQ_ADJUST, "IPS_SEQ_ADJUST"},
      {IPS_SRC_NAT_DONE, "IPS_SRC_NAT_DONE"},
      {IPS_DST_NAT_DONE, "IPS_DST_NAT_DONE"},
      {IPS_NAT_DONE_MASK, "IPS_NAT_DONE_MASK"},
      {IPS_DYING, "IPS_DYING"},
      {IPS_FIXED_TIMEOUT, "IPS_FIXED_TIMEOUT"},
      /* AF_NETLINK isn't currently provided by the socket module, so also list the relevant parameters */
      {AF_NETLINK, "AF_NETLINK"},
      {SOCK_RAW, "SOCK_RAW"},
      {NETLINK_NETFILTER, "NETLINK_NETFILTER"},
      {0, NULL} /* sentinel */
   };

   
   module = Py_InitModule("nlct_", pynlct__methods);
   NfnlError = PyErr_NewException("nfnl.error", NULL, NULL);
   Py_INCREF(NfnlError);
   PyModule_AddObject(module, "error", NfnlError);
   
   NfctHandleType.tp_new = PyType_GenericNew;
   if (PyType_Ready(&NfctHandleType) < 0) return;
   Py_INCREF(&NfctHandleType);
   PyModule_AddObject(module, "NfctHandle", (PyObject*) &NfctHandleType);
   
   for (i = 0; nfct_masks[i].name != NULL; i++) 
      PyModule_AddObject(module, nfct_masks[i].name, Py_BuildValue("i", nfct_masks[i].mask));
   
}

