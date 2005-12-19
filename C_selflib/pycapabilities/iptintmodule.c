#include <Python.h>
#include <libiptc/libiptc.h>
#include <sys/capability.h>

static PyObject *iptintError;

static PyObject * ipt_entry_to_tuple(const struct ipt_entry *p_rule, iptc_handle_t *table_handle) {
   PyObject *iniface_mask = PyTuple_New(IFNAMSIZ);
   PyObject *outiface_mask = PyTuple_New(IFNAMSIZ);
   PyObject *p_result;
   unsigned int i = 0;
   
   while (i < IFNAMSIZ) {
      if (PyTuple_SetItem(iniface_mask, i, Py_BuildValue("b", p_rule->ip.iniface_mask[i])) ||
          PyTuple_SetItem(outiface_mask, i, Py_BuildValue("b", p_rule->ip.outiface_mask[i]))) {
         return NULL;
         }
      i++;
      }
   
   p_result = Py_BuildValue("(NNNNssNNiii)i(NN)()s",
      PyLong_FromUnsignedLong(p_rule->ip.src.s_addr),		/* source ip */
      PyLong_FromUnsignedLong(p_rule->ip.dst.s_addr),		/* destination ip */
      PyLong_FromUnsignedLong(p_rule->ip.smsk.s_addr),		/* source ip mask */
      PyLong_FromUnsignedLong(p_rule->ip.dmsk.s_addr),		/* destination ip mask */
      p_rule->ip.iniface,					/* input device */
      p_rule->ip.outiface,					/* output device */
      iniface_mask,						/* input device mask */
      outiface_mask,						/* output device mask */
      p_rule->ip.proto,						/* ip protocol */
      p_rule->ip.flags,						/* ip flags */
      p_rule->ip.invflags,					/* inverse ip flags */

      p_rule->nfcache,

      PyLong_FromUnsignedLongLong(p_rule->counters.pcnt),	/* packet counter */
      PyLong_FromUnsignedLongLong(p_rule->counters.bcnt),	/* byte counter */
      iptc_get_target(p_rule, table_handle)			/* rule target */
      );
   
   return p_result;
   }
   
   
static PyObject * table_get(PyObject *self, PyObject *args) {
   char *tablename;
   const char *chain_name, *p_policy;
   iptc_handle_t table_handle;
   const struct ipt_entry *p_rule;
   struct ipt_counters counters;
   PyObject *p_rule_list, *p_tuple;
   PyObject *p_chain_dict = PyDict_New();
   
   if (!p_chain_dict) {
      Py_DECREF(args);
      return NULL;
      }

   if (!PyArg_ParseTuple(args, "s", &tablename)) {
      Py_DECREF(args);
      return NULL;
      }
      
   Py_DECREF(args);
   
   if ((table_handle = iptc_init(tablename)) == NULL) {
      PyErr_SetString(iptintError, iptc_strerror(errno));
      return NULL;
      }
   
   for (chain_name = iptc_first_chain(&table_handle) ; chain_name ; chain_name = iptc_next_chain(&table_handle)) {
      p_rule_list = PyList_New(0);
      if (!p_rule_list) {
         iptc_free(&table_handle);
         Py_DECREF(p_rule_list);
         Py_DECREF(p_chain_dict);
         return NULL;
         }
      
      for (p_rule=iptc_first_rule(chain_name, &table_handle) ; p_rule ; p_rule=iptc_next_rule(p_rule, &table_handle)) {
         p_tuple = ipt_entry_to_tuple(p_rule, &table_handle);
         PyList_Append(p_rule_list, p_tuple);
         Py_DECREF(p_tuple);
         }
      
      p_tuple = PyTuple_New(3);
      
      if (iptc_builtin(chain_name, table_handle)) {
         p_policy = iptc_get_policy(chain_name, &counters, &table_handle);
         if (PyTuple_SetItem(p_tuple, 0, Py_BuildValue("s", p_policy)) || PyTuple_SetItem(p_tuple, 1, Py_BuildValue("(NN)", 
                PyLong_FromUnsignedLongLong(counters.pcnt),
                PyLong_FromUnsignedLongLong(counters.bcnt))
                )
            ) {
            iptc_free(&table_handle);
            Py_DECREF(p_rule_list);
            Py_DECREF(p_chain_dict);
            Py_DECREF(p_tuple);
            return NULL;
            }
         } else if (PyTuple_SetItem(p_tuple, 0, Py_BuildValue("")) || PyTuple_SetItem(p_tuple, 1, Py_BuildValue("(NN)",
               Py_BuildValue(""),
               Py_BuildValue("")
              ))
            ) {
            iptc_free(&table_handle);
            Py_DECREF(p_rule_list);
            Py_DECREF(p_chain_dict);
            Py_DECREF(p_tuple);
            return NULL;
            }
         
      if (PyTuple_SetItem(p_tuple, 2, p_rule_list)) {
         iptc_free(&table_handle);
         Py_DECREF(p_chain_dict);
         Py_DECREF(p_tuple);
         return NULL;
         }
         
      if (PyMapping_SetItemString(p_chain_dict, (char*) chain_name, p_tuple)) {
         iptc_free(&table_handle);
         Py_DECREF(p_tuple);
         Py_DECREF(p_chain_dict);
         return NULL;
         }
      Py_DECREF(p_tuple);
      }
   
   iptc_free(&table_handle);
   return p_chain_dict;
   }


static PyMethodDef iptintMethods[] = {
    {"table_get", table_get, METH_VARARGS, "get contents of the specified netfilter table"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initiptint(void) {
    PyObject *module;
    module = Py_InitModule("iptint", iptintMethods);
    iptintError = PyErr_NewException("iptint.error", NULL, NULL);
    Py_INCREF(iptintError);
    PyModule_AddObject(module, "error", iptintError);
}


