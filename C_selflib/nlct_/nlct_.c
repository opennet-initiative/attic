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

struct nfct_handle *nch;
static PyObject *NfnlError;
static PyObject *ct_event_retval = NULL;
int ct_event_pyexc = 0;


static PyObject *ct_dump_conntrack_table(PyObject *self, PyObject *args) {
   int family, srv;
   static PyObject *retval;
   if (!PyArg_ParseTuple(args, "i", &family)) {
      Py_DECREF(args);
      return NULL;
   }
   
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


static PyObject *ct_event_conntrack(PyObject *self, PyObject *args) {
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


struct nfct_mask ct_h_bms(int mask, char *name) {
   struct nfct_mask rv;
   rv.mask = mask;
   rv.name = name;
   return rv;
}


static PyMethodDef pynlct__methods[] = {
   {"ct_dump_conntrack_table", ct_dump_conntrack_table, METH_VARARGS, "nfct_dump_conntrack_table() wrapper"},
   {"ct_event_conntrack", ct_event_conntrack, METH_VARARGS, "nfct_event_conntrack() wrapper"},
   {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
initnlct_(void) {
   int i;
   struct nfct_mask nfct_masks[] = {
      /* see libnetfilter_conntrack.h for the meanings of these */
      /* nfct flag masks 
      ct_h_bms(NFCT_STATUS, "NFCT_STATUS"),
      ct_h_bms(NFCT_PROTOINFO, "NFCT_PROTOINFO"),
      ct_h_bms(NFCT_TIMEOUT, "NFCT_TIMEOUT"),
      ct_h_bms(NFCT_MARK, "NFCT_MARK"),
      ct_h_bms(NFCT_COUNTERS_ORIG, "NFCT_COUNTERS_ORIG"),
      ct_h_bms(NFCT_COUNTERS_RPLY, "NFCT_COUNTERS_RPLY"),
      ct_h_bms(NFCT_USE, "NFCT_USE"),
      ct_h_bms(NFCT_ID, "NFCT_ID"),*/
      /* nfct status masks */
      ct_h_bms(IPS_EXPECTED, "IPS_EXPECTED"),
      ct_h_bms(IPS_SEEN_REPLY, "IPS_SEEN_REPLY"),
      ct_h_bms(IPS_ASSURED, "IPS_ASSURED"),
      ct_h_bms(IPS_CONFIRMED, "IPS_CONFIRMED"),
      ct_h_bms(IPS_SRC_NAT, "IPS_SRC_NAT"),
      ct_h_bms(IPS_DST_NAT, "IPS_DST_NAT"),
      ct_h_bms(IPS_NAT_MASK, "IPS_NAT_MASK"),
      ct_h_bms(IPS_SEQ_ADJUST, "IPS_SEQ_ADJUST"),
      ct_h_bms(IPS_SRC_NAT_DONE, "IPS_SRC_NAT_DONE"),
      ct_h_bms(IPS_DST_NAT_DONE, "IPS_DST_NAT_DONE"),
      ct_h_bms(IPS_NAT_DONE_MASK, "IPS_NAT_DONE_MASK"),
      ct_h_bms(IPS_DYING, "IPS_DYING"),
      ct_h_bms(IPS_FIXED_TIMEOUT, "IPS_FIXED_TIMEOUT"),
      ct_h_bms(0, NULL) /* sentinel */
   };

   nch = nfct_open(CONNTRACK, NFCT_ALL_CT_GROUPS);
   if (!nch) {
      PyErr_SetString(PyExc_ImportError, strerror(errno));
      return;
   }
   fcntl(nfct_fd(nch), F_SETFL, O_NONBLOCK);
   nfct_register_callback(nch, ct_callback, &ct_event_pyexc);
   
   PyObject *module;
   module = Py_InitModule("nlct_", pynlct__methods);
   NfnlError = PyErr_NewException("nfnl.error", NULL, NULL);
   Py_INCREF(NfnlError);
   PyModule_AddObject(module, "error", NfnlError);
   PyModule_AddObject(module, "nch_fd", Py_BuildValue("i",nfct_fd(nch)));
   
   for (i = 0; nfct_masks[i].name != NULL; i++) 
      PyModule_AddObject(module, nfct_masks[i].name, Py_BuildValue("i", nfct_masks[i].mask));
   
}

