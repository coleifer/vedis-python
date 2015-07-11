# Python library for working with Vedis databases.
#        _
#       /.\
#       Y  \
#      /   "L
#     //  "/
#     |/ /\_==================
#     / /
#    / /
#    \/
#
# "Be as a bird perched on a frail branch that she feels bending beneath her,
#  still she sings away all the same, knowing she has wings." - Victor Hugo
#
# Thanks to buaabyl for pyUnQLite, whose source-code helped me get started on
# this library.
from libc.stdlib cimport free, malloc


cdef extern from "src/vedis.h":
    struct vedis
    struct vedis_kv_cursor

    ctypedef struct vedis_context
    ctypedef struct vedis_value

    # Simple types.
    ctypedef signed long long int sxi64
    ctypedef unsigned long long int sxu64
    ctypedef sxi64 vedis_int64

    # Database.
    cdef int vedis_open(vedis **ppStore, const char *zStorage)
    cdef int vedis_config(vedis *pStore, int iOp, ...)
    cdef int vedis_close(vedis *pStore)

    # Command execution.
    cdef int vedis_exec(vedis *pStore, const char *zCmd, int nLen)
    cdef int vedis_exec_fmt(vedis *pStore, const char *zFmt, ...)
    cdef int vedis_exec_result(vedis *pStore, vedis_value **ppOut)

    # Foreign Command Registar
    cdef int vedis_register_command(vedis *pStore, const char *zName, int (*xCmd)(vedis_context *,int,vedis_value **), void *pUserdata)
    cdef int vedis_delete_command(vedis *pStore, const char *zName)

    # Key/Value store.
    cdef int vedis_kv_store(vedis *pDb, const void *pKey, int nKeyLen, const void *pData, vedis_int64 nDataLen)
    cdef int vedis_kv_append(vedis *pDb, const void *pKey, int nKeyLen, const void *pData, vedis_int64 nDataLen)
    cdef int vedis_kv_fetch(vedis *pDb, const void *pKey, int nKeyLen, void *pBuf, vedis_int64 *pSize)
    cdef int vedis_kv_delete(vedis *pDb, const void *pKey, int nKeyLen)
    cdef int vedis_kv_config(vedis *pDb, int iOp, ...)

    # Transactions.
    cdef int vedis_begin(vedis *pDb)
    cdef int vedis_commit(vedis *pDb)
    cdef int vedis_rollback(vedis *pDb)

    # Misc utils.
    cdef int vedis_util_random_string(vedis *pDb, char *zBuf, unsigned int buf_size)
    cdef unsigned int vedis_util_random_num(vedis *pDb)

    # Call Context Key/Value Store Interfaces
    cdef int vedis_context_kv_store(vedis_context *pCtx,const void *pKey,int nKeyLen,const void *pData,vedis_int64 nDataLen)
    cdef int vedis_context_kv_append(vedis_context *pCtx,const void *pKey,int nKeyLen,const void *pData,vedis_int64 nDataLen)
    cdef int vedis_context_kv_store_fmt(vedis_context *pCtx,const void *pKey,int nKeyLen,const char *zFormat,...)
    cdef int vedis_context_kv_append_fmt(vedis_context *pCtx,const void *pKey,int nKeyLen,const char *zFormat,...)
    cdef int vedis_context_kv_fetch(vedis_context *pCtx,const void *pKey,int nKeyLen,void *pBuf,vedis_int64 *pBufLen)
    cdef int vedis_context_kv_delete(vedis_context *pCtx,const void *pKey,int nKeyLen)

    # Command Execution Context Interfaces
    cdef int vedis_context_throw_error(vedis_context *pCtx, int iErr, const char *zErr)
    cdef int vedis_context_throw_error_format(vedis_context *pCtx, int iErr, const char *zFormat, ...)
    cdef void * vedis_context_user_data(vedis_context *pCtx)

    # Setting The Return Value Of A Vedis Command
    cdef int vedis_result_int(vedis_context *pCtx, int iValue)
    cdef int vedis_result_int64(vedis_context *pCtx, vedis_int64 iValue)
    cdef int vedis_result_bool(vedis_context *pCtx, int iBool)
    cdef int vedis_result_double(vedis_context *pCtx, double Value)
    cdef int vedis_result_null(vedis_context *pCtx)
    cdef int vedis_result_string(vedis_context *pCtx, const char *zString, int nLen)
    cdef int vedis_result_string_format(vedis_context *pCtx, const char *zFormat, ...)
    cdef int vedis_result_value(vedis_context *pCtx, vedis_value *pValue)

    # Extracting Vedis Commands Parameter/Return Values
    cdef int vedis_value_to_int(vedis_value *pValue)
    cdef int vedis_value_to_bool(vedis_value *pValue)
    cdef vedis_int64 vedis_value_to_int64(vedis_value *pValue)
    cdef double vedis_value_to_double(vedis_value *pValue)
    cdef const char * vedis_value_to_string(vedis_value *pValue, int *pLen)

    # Dynamically Typed Value Object Query Interfaces
    cdef int vedis_value_is_int(vedis_value *pVal)
    cdef int vedis_value_is_float(vedis_value *pVal)
    cdef int vedis_value_is_bool(vedis_value *pVal)
    cdef int vedis_value_is_string(vedis_value *pVal)
    cdef int vedis_value_is_null(vedis_value *pVal)
    cdef int vedis_value_is_numeric(vedis_value *pVal)
    cdef int vedis_value_is_scalar(vedis_value *pVal)
    cdef int vedis_value_is_array(vedis_value *pVal)

    # Populating dynamically Typed Objects
    cdef int vedis_value_int(vedis_value *pVal, int iValue)
    cdef int vedis_value_int64(vedis_value *pVal, vedis_int64 iValue)
    cdef int vedis_value_bool(vedis_value *pVal, int iBool)
    cdef int vedis_value_null(vedis_value *pVal)
    cdef int vedis_value_double(vedis_value *pVal, double Value)
    cdef int vedis_value_string(vedis_value *pVal, const char *zString, int nLen)
    cdef int vedis_value_string_format(vedis_value *pVal, const char *zFormat, ...)
    cdef int vedis_value_reset_string_cursor(vedis_value *pVal)
    cdef int vedis_value_release(vedis_value *pVal)

    # On-demand Object Value Allocation
    cdef vedis_value * vedis_context_new_scalar(vedis_context *pCtx)
    cdef vedis_value * vedis_context_new_array(vedis_context *pCtx)
    cdef void vedis_context_release_value(vedis_context *pCtx, vedis_value *pValue)

    # Working with Vedis Arrays
    cdef vedis_value * vedis_array_fetch(vedis_value *pArray,unsigned int index)
    cdef int vedis_array_walk(vedis_value *pArray, int (*xWalk)(vedis_value *, void *), void *pUserData)
    cdef int vedis_array_insert(vedis_value *pArray,vedis_value *pValue)
    cdef unsigned int vedis_array_count(vedis_value *pArray)
    cdef int vedis_array_reset(vedis_value *pArray)
    cdef vedis_value * vedis_array_next_elem(vedis_value *pArray)

    # Library info.
    cdef const char * vedis_lib_version()

    cdef int SXRET_OK = 0
    cdef int SXERR_MEM = -1
    cdef int SXERR_IO = -2
    cdef int SXERR_EMPTY = -3
    cdef int SXERR_LOCKED = -4
    cdef int SXERR_ORANGE = -5
    cdef int SXERR_NOTFOUND = -6
    cdef int SXERR_LIMIT = -7
    cdef int SXERR_MORE = -8
    cdef int SXERR_INVALID = -9
    cdef int SXERR_ABORT = -10
    cdef int SXERR_EXISTS = -11
    cdef int SXERR_SYNTAX = -12
    cdef int SXERR_UNKNOWN = -13
    cdef int SXERR_BUSY = -14
    cdef int SXERR_OVERFLOW = -15
    cdef int SXERR_WILLBLOCK = -16
    cdef int SXERR_NOTIMPLEMENTED = -17
    cdef int SXERR_EOF = -18
    cdef int SXERR_PERM = -19
    cdef int SXERR_NOOP = -20
    cdef int SXERR_FORMAT = -21
    cdef int SXERR_NEXT = -22
    cdef int SXERR_OS = -23
    cdef int SXERR_CORRUPT = -24
    cdef int SXERR_CONTINUE = -25
    cdef int SXERR_NOMATCH = -26
    cdef int SXERR_RESET = -27
    cdef int SXERR_DONE = -28
    cdef int SXERR_SHORT = -29
    cdef int SXERR_PATH = -30
    cdef int SXERR_TIMEOUT = -31
    cdef int SXERR_BIG = -32
    cdef int SXERR_RETRY = -33
    cdef int SXERR_IGNORE = -63

    # Vedis return values and error codes.
    cdef int VEDIS_OK = SXRET_OK

    # Errors.
    cdef int VEDIS_NOMEM = SXERR_MEM  # Out of memory
    cdef int VEDIS_ABORT = SXERR_ABORT  # Another thread have released this instance
    cdef int VEDIS_IOERR = SXERR_IO  # IO error
    cdef int VEDIS_CORRUPT = SXERR_CORRUPT  # Corrupt pointer
    cdef int VEDIS_LOCKED = SXERR_LOCKED  # Forbidden Operation
    cdef int VEDIS_BUSY = SXERR_BUSY  # The database file is locked
    cdef int VEDIS_DONE = SXERR_DONE  # Operation done
    cdef int VEDIS_PERM = SXERR_PERM  # Permission error
    cdef int VEDIS_NOTIMPLEMENTED = SXERR_NOTIMPLEMENTED  # Method not implemented by the underlying Key/Value storage engine
    cdef int VEDIS_NOTFOUND = SXERR_NOTFOUND  # No such record
    cdef int VEDIS_NOOP = SXERR_NOOP  # No such method
    cdef int VEDIS_INVALID = SXERR_INVALID  # Invalid parameter
    cdef int VEDIS_EOF = SXERR_EOF  # End Of Input
    cdef int VEDIS_UNKNOWN = SXERR_UNKNOWN  # Unknown configuration option
    cdef int VEDIS_LIMIT = SXERR_LIMIT  # Database limit reached
    cdef int VEDIS_EXISTS = SXERR_EXISTS  # Record exists
    cdef int VEDIS_EMPTY = SXERR_EMPTY  # Empty record
    cdef int VEDIS_FULL = (-73)  # Full database (unlikely)
    cdef int VEDIS_CANTOPEN = (-74)  # Unable to open the database file
    cdef int VEDIS_READ_ONLY = (-75)  # Read only Key/Value storage engine
    cdef int VEDIS_LOCKERR = (-76)  # Locking protocol error

    # Database config commands.
    cdef int VEDIS_CONFIG_ERR_LOG = 1
    cdef int VEDIS_CONFIG_MAX_PAGE_CACHE = 2
    cdef int VEDIS_CONFIG_KV_ENGINE = 4
    cdef int VEDIS_CONFIG_DISABLE_AUTO_COMMIT = 5
    cdef int VEDIS_CONFIG_GET_KV_NAME = 6
    cdef int VEDIS_CONFIG_DUP_EXEC_VALUE = 7
    cdef int VEDIS_CONFIG_RELEASE_DUP_VALUE = 8
    cdef int VEDIS_CONFIG_OUTPUT_CONSUMER = 9

    # Cursor seek flags.
    cdef int VEDIS_CURSOR_MATCH_EXACT = 1
    cdef int VEDIS_CURSOR_MATCH_LE = 2
    cdef int VEDIS_CURSOR_MATCH_GE = 3


cdef class Vedis(object):
    """
    Vedis database wrapper.
    """
    cdef vedis *database
    cdef readonly bint is_memory
    cdef readonly bint is_open
    cdef readonly basestring filename
    cdef bint open_database

    def __cinit__(self):
        self.database = <vedis *>0
        self.is_memory = False
        self.is_open = False

    def __dealloc__(self):
        if self.is_open:
            vedis_close(self.database)

    def __init__(self, filename=':mem:', open_database=True):
        self.filename = filename
        self.is_memory = filename == ':mem:'
        self.open_database = open_database
        if self.open_database:
            self.open()

    cpdef open(self):
        """Open database connection."""
        cdef int ret

        if self.is_open:
            self.close()

        self.check_call(vedis_open(
            &self.database,
            self.filename))

        self.is_open = True

    cpdef close(self):
        """Close database connection."""
        if self.is_open:
            self.check_call(vedis_close(self.database))
            self.is_open = 0
            self.database = <vedis *>0

    def __enter__(self):
        """Use database connection as a context manager."""
        if not self.is_open:
            self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    cpdef disable_autocommit(self):
        if not self.is_memory:
            # Disable autocommit for file-based databases.
            ret = vedis_config(
                self.database,
                VEDIS_CONFIG_DISABLE_AUTO_COMMIT)
            if ret != VEDIS_OK:
                raise NotImplementedError('Error disabling autocommit for '
                                          'in-memory database.')

    cpdef store(self, basestring key, basestring value):
        """Store key/value."""
        self.check_call(vedis_kv_store(
            self.database,
            <const char *>key,
            -1,
            <const char *>value,
            len(value)))

    cpdef fetch(self, basestring key):
        """Retrieve value at given key. Raises `KeyError` if key not found."""
        cdef char *buf = <char *>0
        cdef vedis_int64 buf_size = 0

        self.check_call(vedis_kv_fetch(
            self.database,
            <char *>key,
            -1,
            <void *>0,
            &buf_size))

        try:
            buf = <char *>malloc(buf_size)
            self.check_call(vedis_kv_fetch(
                self.database,
                <char *>key,
                -1,
                <void *>buf,
                &buf_size))

            return buf[:buf_size]
        finally:
            free(buf)

    cpdef delete(self, basestring key):
        """Delete the value stored at the given key."""
        self.check_call(vedis_kv_delete(self.database, <char *>key, -1))

    cpdef append(self, basestring key, basestring value):
        """Append to the value stored in the given key."""
        self.check_call(vedis_kv_append(
            self.database,
            <const char *>key,
            -1,
            <const char *>value,
            len(value)))

    cpdef exists(self, basestring key):
        cdef char *buf = <char *>0
        cdef vedis_int64 buf_size = 0
        cdef int ret

        ret = vedis_kv_fetch(
            self.database,
            <char *>key,
            -1,
            <void *>0,
            &buf_size)
        if ret == VEDIS_NOTFOUND:
            return False
        elif ret == VEDIS_OK:
            return True

        raise self._build_exception_for_error(ret)

    def __setitem__(self, basestring key, basestring value):
        self.store(key, value)

    def __getitem__(self, basestring key):
        return self.fetch(key)

    def __delitem__(self, basestring key):
        self.delete(key)

    def __contains__(self, basestring key):
        return self.exists(key)

    cpdef execute(self, basestring cmd, tuple params=None, bint result=False):
        cdef list escaped_params
        if params is not None:
            escaped_params = [self._escape(p) for p in params]
            cmd = cmd % tuple(escaped_params)
        self.check_call(vedis_exec(self.database, <const char *>cmd, -1))
        if result:
            return self.get_result()

    cpdef get_result(self):
        cdef vedis_value* value = <vedis_value *>0
        vedis_exec_result(self.database, &value)
        return vedis_value_to_python(value)

    cdef check_call(self, int result):
        """
        Check for a successful Vedis library call, raising an exception
        if the result is other than `VEDIS_OK`.
        """
        if result != VEDIS_OK:
            raise self._build_exception_for_error(result)

    cdef _build_exception_for_error(self, int status):
        cdef dict exc_map

        exc_map = {
            VEDIS_NOMEM: MemoryError,
            VEDIS_IOERR: IOError,
            VEDIS_CORRUPT: IOError,
            VEDIS_LOCKED: IOError,
            VEDIS_BUSY: IOError,
            VEDIS_LOCKERR: IOError,
            VEDIS_NOTIMPLEMENTED: NotImplementedError,
            VEDIS_NOTFOUND: KeyError,
            VEDIS_NOOP: NotImplementedError,
            VEDIS_EOF: IOError,
            VEDIS_FULL: IOError,
            VEDIS_CANTOPEN: IOError,
            VEDIS_READ_ONLY: IOError,
        }

        exc_klass = exc_map.get(status, Exception)
        if status != VEDIS_NOTFOUND:
            message = self._get_last_error()
            return exc_klass(message)
        else:
            return exc_klass()

    cdef _get_last_error(self):
        cdef int ret
        cdef int size
        cdef char buf[1024]

        ret = vedis_config(
            self.database,
            VEDIS_CONFIG_ERR_LOG,
            &buf,
            &size)
        if ret != VEDIS_OK:
            return None

        return buf[:size]

    cpdef begin(self):
        """Begin a new transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(vedis_begin(self.database))

    cpdef commit(self):
        """Commit current transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(vedis_commit(self.database))

    cpdef rollback(self):
        """Rollback current transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(vedis_rollback(self.database))

    def transaction(self):
        """Create context manager for wrapping a transaction."""
        return Transaction(self)

    def commit_on_success(self, fn):
        def wrapper(*args, **kwargs):
            with self.transaction():
                return fn(*args, **kwargs)
        return wrapper

    cpdef update(self, dict values):
        cdef basestring key
        for key in values:
            self.store(key, values[key])

    cpdef random_string(self, int nbytes):
        """Generate a random string of given length."""
        cdef char *buf
        buf = <char *>malloc(nbytes * sizeof(char))
        try:
            vedis_util_random_string(self.database, buf, nbytes)
            return buf[:nbytes]
        finally:
            free(buf)

    cpdef int random_int(self):
        """Generate a random integer."""
        return vedis_util_random_num(self.database)

    cdef basestring _flatten_list(self, list args):
        return ' '.join(map(self._escape, args))

    cdef basestring _flatten(self, dict kwargs):
        cdef basestring key
        return ' '.join(
            '%s %s' % (self._escape(key), self._escape(kwargs[key]))
            for key in kwargs)

    cdef basestring _escape(self, basestring s):
        return '"%s"' % str(s).replace('"', '\\"')

    cpdef int strlen(self, basestring key):
        return self.execute('STRLEN %s', (key,), True)

    cpdef copy(self, basestring src, basestring dest):
        return self.execute('COPY %s %s', (src, dest), True)

    cpdef move(self, basestring src, basestring dest):
        return self.execute('MOVE %s %s', (src, dest), True)

    def lib_version(self):
        return vedis_lib_version()


cdef class Transaction(object):
    """Expose transaction as a context manager."""
    cdef Vedis vedis

    def __init__(self, vedis):
        self.vedis = vedis

    def __enter__(self):
        self.vedis.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.vedis.rollback()
        else:
            try:
                self.vedis.commit()
            except:
                self.vedis.rollback()
                raise


cdef vedis_value_to_python(vedis_value *ptr):
    cdef int nbytes
    cdef list accum
    cdef vedis_value *item = <vedis_value *>0

    if vedis_value_is_string(ptr):
        return str(vedis_value_to_string(ptr, &nbytes))[:nbytes]
    elif vedis_value_is_array(ptr):
        accum = []
        while True:
            item = vedis_array_next_elem(ptr)
            if not item:
                break
            accum.append(vedis_value_to_python(item))
        return accum
    elif vedis_value_is_int(ptr):
        return vedis_value_to_int(ptr)
    elif vedis_value_is_float(ptr):
        return vedis_value_to_double(ptr)
    elif vedis_value_is_bool(ptr):
        return bool(vedis_value_to_bool(ptr))
    elif vedis_value_is_null(ptr):
        return None
    raise TypeError('Unrecognized type.')


cdef vedis_value* python_to_vedis_value(vedis_context *context, python_value):
    if isinstance(python_value, (list, tuple)):
        return create_vedis_array(context, python_value)
    else:
        return create_vedis_scalar(context, python_value)


cdef vedis_value* create_vedis_scalar(vedis_context *context, python_value):
    cdef vedis_value *ptr
    ptr = vedis_context_new_scalar(context)
    if isinstance(python_value, unicode):
        vedis_value_string(ptr, python_value.encode('utf-8'), -1)
    elif isinstance(python_value, basestring):
        vedis_value_string(ptr, python_value, -1)
    elif isinstance(python_value, (int, long)):
        vedis_value_int(ptr, python_value)
    elif isinstance(python_value, bool):
        vedis_value_bool(ptr, python_value)
    elif isinstance(python_value, float):
        vedis_value_double(ptr, python_value)
    elif python_value is None:
        vedis_value_null(ptr)
    else:
        raise TypeError('Unsupported type: %s.' % type(python_value))


cdef vedis_value* create_vedis_array(vedis_context *context, list items):
    cdef vedis_value *ptr
    cdef vedis_value *list_item
    ptr = vedis_context_new_array(context)
    for item in items:
        list_item = python_to_vedis_value(context, item)
        vedis_array_insert(ptr, list_item)
    return ptr


cdef push_result(vedis_context *context, python_value):
    if isinstance(python_value, unicode):
        vedis_result_string(context, python_value.encode('utf-8'), -1)
    elif isinstance(python_value, basestring):
        vedis_result_string(context, python_value, -1)
    elif isinstance(python_value, (list, tuple)):
        vedis_result_value(context, create_vedis_array(context, python_value))
    elif isinstance(python_value, (int, long)):
        vedis_result_int(context, python_value)
    elif isinstance(python_value, bool):
        vedis_result_bool(context, python_value)
    elif isinstance(python_value, float):
        vedis_result_double(context, python_value)
    else:
        vedis_result_null(context)
