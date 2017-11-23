
#include <Python.h>
#include <sys/capability.h>
#include <sys/prctl.h>

static PyObject *CapabilitiesError;

static PyObject * py_prctl(PyObject *self, PyObject *args) {
   int option, retval;
   unsigned long arg2, arg3, arg4, arg5;
   if (!PyArg_ParseTuple(args, "ikkkk", &option, &arg2, &arg3, &arg4, &arg5)) {
      Py_DECREF(args);
      return NULL;
   }
      
   Py_DECREF(args);

   retval = prctl(option, arg2, arg3 , arg4, arg5);
   if (retval == -1) {
      PyErr_SetString(CapabilitiesError, strerror(errno));
      return NULL;
   } else if (option == PR_GET_PDEATHSIG) {
      return Py_BuildValue("i", arg2);
   } else {
      return Py_BuildValue("i", retval);
   }
}

static PyObject * py_cap_get(PyObject *self, PyObject *args) {
   char *cap_p;
   cap_t capability_set;
   PyObject *return_string;
   Py_DECREF(args);
   capability_set = cap_get_proc();
   if (capability_set == NULL) {
      PyErr_SetString(CapabilitiesError, strerror(errno));
      return NULL;
      }
   cap_p = cap_to_text(capability_set, NULL);
   if (cap_p == NULL) {
      PyErr_SetString(CapabilitiesError, strerror(errno));
      cap_free(cap_p);
      return NULL;
      }
   return_string = Py_BuildValue("s", cap_p);
   cap_free(cap_p);
   return return_string;
}

static PyObject * py_cap_set(PyObject *self, PyObject *args) {
   char *capability_string;
   if (!PyArg_ParseTuple(args, "s", &capability_string)) {
      Py_DECREF(args);
      return NULL;
   }

   Py_DECREF(args);
   
   cap_t capability_state = cap_from_text(capability_string);
   
   if ((capability_state == NULL) || (cap_set_proc(capability_state))) {
      cap_free(capability_state);
      PyErr_SetString(CapabilitiesError, strerror(errno));
      return NULL;
   }
   cap_free(capability_state);
   Py_INCREF(Py_True);
   return Py_True;
}

static PyMethodDef iptintMethods[] = {
    {"prctl", py_prctl, METH_VARARGS, "prctl() wrapper"},
    {"cap_get", py_cap_get, METH_VARARGS, "cap_to_text(cap_get_proc()) wrapper"},
    {"cap_set", py_cap_set, METH_VARARGS, "cap_set_proc(cap_from_text()) wrapper"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpycapabilities(void) {
    PyObject *module;
    module = Py_InitModule("pycapabilities", iptintMethods);
    CapabilitiesError = PyErr_NewException("pycapabilities.error", NULL, NULL);
    Py_INCREF(CapabilitiesError);
    PyModule_AddObject(module, "error", CapabilitiesError);
    PyModule_AddObject(module, "PR_GET_PDEATHSIG", Py_BuildValue("i", PR_GET_PDEATHSIG));
    PyModule_AddObject(module, "PR_SET_PDEATHSIG", Py_BuildValue("i", PR_SET_PDEATHSIG));
    PyModule_AddObject(module, "PR_GET_DUMPABLE", Py_BuildValue("i", PR_GET_DUMPABLE));
    PyModule_AddObject(module, "PR_SET_DUMPABLE", Py_BuildValue("i", PR_SET_DUMPABLE));
    PyModule_AddObject(module, "PR_GET_KEEPCAPS", Py_BuildValue("i", PR_GET_KEEPCAPS));
    PyModule_AddObject(module, "PR_SET_KEEPCAPS", Py_BuildValue("i", PR_SET_KEEPCAPS));
}


