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
    cdef int unqlite_util_random_string(unqlite *pDb, char *zBuf, unsigned int buf_size)
    cdef unsigned int unqlite_util_random_num(unqlite *pDb)

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

    # Constant values (http://unqlite.org/c_api_const.html).
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
    cdef VEDIS_NOMEM = SXERR_MEM  # Out of memory
    cdef VEDIS_ABORT = SXERR_ABORT  # Another thread have released this instance
    cdef VEDIS_IOERR = SXERR_IO  # IO error
    cdef VEDIS_CORRUPT = SXERR_CORRUPT  # Corrupt pointer
    cdef VEDIS_LOCKED = SXERR_LOCKED  # Forbidden Operation
    cdef VEDIS_BUSY = SXERR_BUSY  # The database file is locked
    cdef VEDIS_DONE = SXERR_DONE  # Operation done
    cdef VEDIS_PERM = SXERR_PERM  # Permission error
    cdef VEDIS_NOTIMPLEMENTED = SXERR_NOTIMPLEMENTED  # Method not implemented by the underlying Key/Value storage engine
    cdef VEDIS_NOTFOUND = SXERR_NOTFOUND  # No such record
    cdef VEDIS_NOOP = SXERR_NOOP  # No such method
    cdef VEDIS_INVALID = SXERR_INVALID  # Invalid parameter
    cdef VEDIS_EOF = SXERR_EOF  # End Of Input
    cdef VEDIS_UNKNOWN = SXERR_UNKNOWN  # Unknown configuration option
    cdef VEDIS_LIMIT = SXERR_LIMIT  # Database limit reached
    cdef VEDIS_EXISTS = SXERR_EXISTS  # Record exists
    cdef VEDIS_EMPTY = SXERR_EMPTY  # Empty record
    cdef VEDIS_FULL = (-73)  # Full database (unlikely)
    cdef VEDIS_CANTOPEN = (-74)  # Unable to open the database file
    cdef VEDIS_READ_ONLY = (-75)  # Read only Key/Value storage engine
    cdef VEDIS_LOCKERR = (-76)  # Locking protocol error

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


cdef class UnQLite(object):
    """
    UnQLite database wrapper.
    """
    cdef unqlite *database
    cdef readonly bint is_memory
    cdef readonly bint is_open
    cdef readonly basestring filename
    cdef readonly int flags
    cdef bint open_database

    def __cinit__(self):
        self.database = <unqlite *>0
        self.is_memory = False
        self.is_open = False

    def __dealloc__(self):
        if self.is_open:
            unqlite_close(self.database)

    def __init__(self, filename=':mem:', flags=UNQLITE_OPEN_CREATE,
                 open_database=True):
        self.filename = filename
        self.flags = flags
        self.is_memory = filename == ':mem:'
        self.open_database = open_database
        if self.open_database:
            self.open()

    def open(self):
        """Open database connection."""
        cdef int ret

        if self.is_open:
            self.close()

        self.check_call(unqlite_open(
            &self.database,
            self.filename,
            self.flags))

        self.is_open = True

    def close(self):
        """Close database connection."""
        if self.is_open:
            self.check_call(unqlite_close(self.database))
            self.is_open = 0
            self.database = <unqlite *>0

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
            ret = unqlite_config(
                self.database,
                UNQLITE_CONFIG_DISABLE_AUTO_COMMIT)
            if ret != UNQLITE_OK:
                raise NotImplementedError('Error disabling autocommit for '
                                          'in-memory database.')

    cpdef store(self, basestring key, basestring value):
        """Store key/value."""
        self.check_call(unqlite_kv_store(
            self.database,
            <const char *>key,
            -1,
            <const char *>value,
            len(value)))

    cpdef fetch(self, basestring key):
        """Retrieve value at given key. Raises `KeyError` if key not found."""
        cdef char *buf = <char *>0
        cdef unqlite_int64 buf_size = 0

        self.check_call(unqlite_kv_fetch(
            self.database,
            <char *>key,
            -1,
            <void *>0,
            &buf_size))

        try:
            buf = <char *>malloc(buf_size)
            self.check_call(unqlite_kv_fetch(
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
        self.check_call(unqlite_kv_delete(self.database, <char *>key, -1))

    cpdef append(self, basestring key, basestring value):
        """Append to the value stored in the given key."""
        self.check_call(unqlite_kv_append(
            self.database,
            <const char *>key,
            -1,
            <const char *>value,
            len(value)))

    cpdef exists(self, basestring key):
        cdef char *buf = <char *>0
        cdef unqlite_int64 buf_size = 0
        cdef int ret

        ret = unqlite_kv_fetch(
            self.database,
            <char *>key,
            -1,
            <void *>0,
            &buf_size)
        if ret == UNQLITE_NOTFOUND:
            return False
        elif ret == UNQLITE_OK:
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

    cdef check_call(self, int result):
        """
        Check for a successful UnQLite library call, raising an exception
        if the result is other than `UNQLITE_OK`.
        """
        if result != UNQLITE_OK:
            raise self._build_exception_for_error(result)

    cdef _build_exception_for_error(self, int status):
        cdef dict exc_map

        exc_map = {
            UNQLITE_NOMEM: MemoryError,
            UNQLITE_IOERR: IOError,
            UNQLITE_CORRUPT: IOError,
            UNQLITE_LOCKED: IOError,
            UNQLITE_BUSY: IOError,
            UNQLITE_LOCKERR: IOError,
            UNQLITE_NOTIMPLEMENTED: NotImplementedError,
            UNQLITE_NOTFOUND: KeyError,
            UNQLITE_NOOP: NotImplementedError,
            UNQLITE_EOF: IOError,
            UNQLITE_FULL: IOError,
            UNQLITE_CANTOPEN: IOError,
            UNQLITE_READ_ONLY: IOError,
        }

        exc_klass = exc_map.get(status, Exception)
        if status != UNQLITE_NOTFOUND:
            message = self._get_last_error()
            return exc_klass(message)
        else:
            return exc_klass()

    cdef _get_last_error(self):
        cdef int ret
        cdef int size
        cdef char buf[1024]

        ret = unqlite_config(
            self.database,
            UNQLITE_CONFIG_ERR_LOG,
            &buf,
            &size)
        if ret != UNQLITE_OK:
            return None

        return buf[:size]

    cpdef begin(self):
        """Begin a new transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(unqlite_begin(self.database))

    cpdef commit(self):
        """Commit current transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(unqlite_commit(self.database))

    cpdef rollback(self):
        """Rollback current transaction. Only works for file-based databases."""
        if self.is_memory:
            return

        self.check_call(unqlite_rollback(self.database))

    def transaction(self):
        """Create context manager for wrapping a transaction."""
        return Transaction(self)

    def commit_on_success(self, fn):
        def wrapper(*args, **kwargs):
            with self.transaction():
                return fn(*args, **kwargs)
        return wrapper

    def cursor(self):
        """Create a cursor for iterating through the database."""
        return Cursor(self)

    def vm(self, basestring code):
        """Create an UnQLite Jx9 virtual machine."""
        return VM(self, code)

    def collection(self, basestring name):
        """Create a wrapper for working with Jx9 collections."""
        return Collection(self, name)

    cpdef update(self, dict values):
        cdef basestring key
        for key in values:
            self.store(key, values[key])

    def keys(self):
        """Efficiently iterate through the database's keys."""
        cdef Cursor cursor
        with self.cursor() as cursor:
            while cursor.is_valid():
                yield cursor.key()
                try:
                    cursor.next_entry()
                except StopIteration:
                    break

    def values(self):
        """Efficiently iterate through the database's values."""
        cdef Cursor cursor
        with self.cursor() as cursor:
            while cursor.is_valid():
                yield cursor.value()
                try:
                    cursor.next_entry()
                except StopIteration:
                    break

    def items(self):
        """Efficiently iterate through the database's key/value pairs."""
        cdef Cursor cursor
        cdef tuple item

        with self.cursor() as cursor:
            for item in cursor:
                yield item

    def __iter__(self):
        cursor = self.cursor()
        cursor.reset()
        return cursor

    def range(self, basestring start_key, basestring end_key,
                bint include_end_key=True):
        cdef Cursor cursor = self.cursor()
        cursor.seek(start_key)
        for item in cursor.fetch_until(end_key, include_end_key):
            yield item

    def __len__(self):
        """
        Return the total number of records in the database.

        Note: this operation is O(n) and requires iterating through the
        entire key-space.
        """
        cdef Cursor cursor
        cdef long count = 0
        with self.cursor() as cursor:
            for item in cursor:
                count += 1
        return count

    def flush(self):
        """
        Remove all records from the database.

        Note: this operation is O(n) and requires iterating through the
        entire key-space.
        """
        cdef Cursor cursor
        cdef long i = 0
        with self.cursor() as cursor:
            while cursor.is_valid():
                cursor.delete()
                i += 1
        return i

    cpdef random_string(self, int nbytes):
        """Generate a random string of given length."""
        cdef char *buf
        buf = <char *>malloc(nbytes * sizeof(char))
        try:
            unqlite_util_random_string(self.database, buf, nbytes)
            return buf[:nbytes]
        finally:
            free(buf)

    cpdef int random_int(self):
        """Generate a random integer."""
        return unqlite_util_random_num(self.database)

    def lib_version(self):
        return unqlite_lib_version()


cdef class Transaction(object):
    """Expose transaction as a context manager."""
    cdef UnQLite unqlite

    def __init__(self, unqlite):
        self.unqlite = unqlite

    def __enter__(self):
        self.unqlite.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.unqlite.rollback()
        else:
            try:
                self.unqlite.commit()
            except:
                self.unqlite.rollback()
                raise


cdef class Cursor(object):
    """Cursor interface for efficiently iterating through database."""
    cdef UnQLite unqlite
    cdef unqlite_kv_cursor *cursor
    cdef bint consumed

    def __cinit__(self, unqlite):
        self.unqlite = unqlite
        self.cursor = <unqlite_kv_cursor *>0
        unqlite_kv_cursor_init(self.unqlite.database, &self.cursor)

    def __dealloc__(self):
        unqlite_kv_cursor_release(self.unqlite.database, self.cursor)

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    cpdef reset(self):
        """Reset the cursor's position."""
        unqlite_kv_cursor_reset(self.cursor)

    cpdef seek(self, basestring key, int flags=UNQLITE_CURSOR_MATCH_EXACT):
        """
        Seek to the given key. The flags specify how UnQLite will determine
        when to stop. Values are:

        * UNQLITE_CURSOR_MATCH_EXACT (default).
        * UNQLITE_CURSOR_MATCH_LE
        * UNQLITE_CURSOR_MATCH_GE
        """
        self.unqlite.check_call(unqlite_kv_cursor_seek(
            self.cursor,
            <char *>key,
            -1,
            flags))

    cpdef first(self):
        """Set cursor to the first record in the database."""
        self.unqlite.check_call(unqlite_kv_cursor_first_entry(self.cursor))

    cpdef last(self):
        """Set cursor to the last record in the database."""
        self.unqlite.check_call(unqlite_kv_cursor_last_entry(self.cursor))

    cpdef next_entry(self):
        """Move cursor to the next entry."""
        cdef int ret
        ret = unqlite_kv_cursor_next_entry(self.cursor)
        if ret != UNQLITE_OK:
            raise StopIteration

    cpdef previous_entry(self):
        """Move cursor to the previous entry."""
        cdef int ret
        ret = unqlite_kv_cursor_prev_entry(self.cursor)
        if ret != UNQLITE_OK:
            raise StopIteration

    cpdef bint is_valid(self):
        """
        Return a boolean value indicating whether the cursor is currently
        pointing to a valid record.
        """
        if unqlite_kv_cursor_valid_entry(self.cursor):
            return True
        return False

    def __iter__(self):
        self.consumed = False
        return self

    cpdef key(self):
        """Retrieve the key at the cursor's current location."""
        cdef int ret
        cdef int key_size
        cdef char *key

        self.unqlite.check_call(
            unqlite_kv_cursor_key(self.cursor, <void *>0, &key_size))

        try:
            key = <char *>malloc(key_size * sizeof(char))
            unqlite_kv_cursor_key(
                self.cursor,
                <char *>key,
                &key_size)

            return key[:key_size]
        finally:
            free(key)

    cpdef value(self):
        """Retrieve the value at the cursor's current location."""
        cdef int ret
        cdef unqlite_int64 value_size
        cdef char *value

        self.unqlite.check_call(
            unqlite_kv_cursor_data(self.cursor, <void *>0, &value_size))

        try:
            value = <char *>malloc(value_size * sizeof(char))
            unqlite_kv_cursor_data(
                self.cursor,
                <char *>value,
                &value_size)

            return value[:value_size]
        finally:
            free(value)

    cpdef delete(self):
        """Delete the record at the cursor's current location."""
        self.unqlite.check_call(unqlite_kv_cursor_delete_entry(self.cursor))

    def __next__(self):
        cdef int ret
        cdef basestring key, value

        if self.consumed:
            raise StopIteration

        try:
            key = self.key()
            value = self.value()
        except:
            raise StopIteration
        else:
            ret = unqlite_kv_cursor_next_entry(self.cursor)
            if ret != UNQLITE_OK:
                self.consumed = True

        return (key, value)

    def fetch_until(self, basestring stop_key, bint include_stop_key=True):
        cdef basestring key

        for key, value in self:
            if key == stop_key:
                if include_stop_key:
                    yield (key, value)
                raise StopIteration
            else:
                yield (key, value)


# Foreign function callback signature.
ctypedef int (*unqlite_filter_fn)(unqlite_context *, int, unqlite_value **)


cdef class VM(object):
    """Jx9 virtual-machine interface."""
    cdef UnQLite unqlite
    cdef unqlite_vm *vm
    cdef readonly basestring code

    def __cinit__(self, UnQLite unqlite, basestring code):
        self.unqlite = unqlite
        self.vm = <unqlite_vm *>0
        self.code = code

    def __dealloc__(self):
        # For some reason, calling unqlite_vm_release() here always causes a
        # segfault.
        pass

    cpdef compile(self):
        """Compile the Jx9 script."""
        self.unqlite.check_call(unqlite_compile(
            self.unqlite.database,
            <const char *>self.code,
            -1,
            &self.vm))

    cpdef execute(self):
        """Execute the compiled Jx9 script."""
        unqlite_vm_exec(self.vm)

    cpdef close(self):
        """Close and release the virtual machine."""
        unqlite_vm_release(self.vm)

    def __enter__(self):
        self.compile()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    cdef unqlite_value* create_value(self, value):
        """
        Create an `unqlite_value` corresponding to the given Python value.
        """
        cdef unqlite_value *ptr
        if isinstance(value, (list, tuple, dict)):
            ptr = self.create_array()
        else:
            ptr = self.create_scalar()
        python_to_unqlite_value(self, ptr, value)
        return ptr

    cdef release_value(self, unqlite_value *ptr):
        """Release the given `unqlite_value`."""
        self.unqlite.check_call(unqlite_vm_release_value(self.vm, ptr))

    cdef unqlite_value* create_array(self):
        return unqlite_vm_new_array(self.vm)

    cdef unqlite_value* create_scalar(self):
        return unqlite_vm_new_scalar(self.vm)

    def set_value(self, name, value):
        """Set the value of a variable in the Jx9 script."""
        cdef unqlite_value *ptr
        ptr = self.create_value(value)
        self.unqlite.check_call(unqlite_vm_config(
            self.vm,
            UNQLITE_VM_CONFIG_CREATE_VAR,
            <const char *>name,
            ptr))
        self.release_value(ptr)

    def get_value(self, name):
        """
        Retrieve the value of a variable after the execution of the
        Jx9 script.
        """
        cdef unqlite_value *ptr

        ptr = unqlite_vm_extract_variable(self.vm, name)
        try:
            return unqlite_value_to_python(ptr)
        finally:
            self.release_value(ptr)

    def __getitem__(self, name):
        return self.get_value(name)

    def __setitem__(self, name, value):
        self.set_value(name, value)


cdef class Context(object):
    cdef unqlite_context *context

    def __cinit__(self):
        self.context = NULL

    cdef set_context(self, unqlite_context *context):
        self.context = context

    cdef unqlite_value * create_value(self, value):
        cdef unqlite_value *ptr

        if isinstance(value, (list, tuple, dict)):
            ptr = self.create_array()
        else:
            ptr = self.create_scalar()

        self.python_to_unqlite_value(ptr, value)
        return ptr

    cdef release_value(self, unqlite_value *ptr):
        unqlite_context_release_value(self.context, ptr)

    cdef unqlite_value* create_array(self):
        return unqlite_context_new_array(self.context)

    cdef unqlite_value* create_scalar(self):
        return unqlite_context_new_scalar(self.context)

    cpdef push_result(self, value):
        cdef unqlite_value *ptr
        ptr = self.create_value(value)
        unqlite_result_value(self.context, ptr)
        self.release_value(ptr)

    cdef python_to_unqlite_value(self, unqlite_value *ptr, python_value):
        cdef unqlite_value *item_ptr = <unqlite_value *>0

        if isinstance(python_value, unicode):
            unqlite_value_string(ptr, python_value.encode('utf-8'), -1)
        elif isinstance(python_value, basestring):
            unqlite_value_string(ptr, python_value, -1)
        elif isinstance(python_value, (list, tuple)):
            for item in python_value:
                item_ptr = self.create_value(item)
                unqlite_array_add_elem(ptr, NULL, item_ptr)
                self.release_value(item_ptr)
        elif isinstance(python_value, dict):
            for key, value in python_value.items():
                if isinstance(key, unicode):
                    key = key.encode('utf-8')
                item_ptr = self.create_value(value)
                unqlite_array_add_strkey_elem(
                    ptr,
                    key,
                    item_ptr)
                self.release_value(item_ptr)
        elif isinstance(python_value, (int, long)):
            unqlite_value_int(ptr, python_value)
        elif isinstance(python_value, bool):
            unqlite_value_bool(ptr, python_value)
        elif isinstance(python_value, float):
            unqlite_value_double(ptr, python_value)
        else:
            unqlite_value_null(ptr)


cdef object py_filter_fn = None

cdef int py_filter_wrapper(unqlite_context *context, int nargs, unqlite_value **values):
    cdef int i
    cdef list converted = []
    cdef Context context_wrapper = Context()

    context_wrapper.set_context(context)

    for i in range(nargs):
        converted.append(unqlite_value_to_python(values[i]))

    try:
        ret = py_filter_fn(*converted)
    except:
        return UNQLITE_ABORT
    else:
        context_wrapper.push_result(ret)
        return UNQLITE_OK


cdef class Collection(object):
    """
    Manage collections of UnQLite JSON documents.
    """
    cdef UnQLite unqlite
    cdef basestring name

    def __init__(self, UnQLite unqlite, basestring name):
        self.unqlite = unqlite
        self.name = name

    def _execute(self, basestring script, **kwargs):
        cdef VM vm
        with VM(self.unqlite, script) as vm:
            vm['collection'] = self.name
            for key, value in kwargs.items():
                vm[key] = value
            vm.execute()

    def _simple_execute(self, basestring script, **kwargs):
        cdef VM vm
        with VM(self.unqlite, script) as vm:
            vm['collection'] = self.name
            for key, value in kwargs.items():
                vm[key] = value
            vm.execute()
            return vm['ret']

    def all(self):
        """Retrieve all records in the given collection."""
        return self._simple_execute('$ret = db_fetch_all($collection);')

    cpdef filter(self, filter_fn):
        """
        Filter the records in the collection using the provided Python
        callback.
        """
        cdef unqlite_filter_fn filter_callback
        cdef VM vm
        global py_filter_fn

        script = '$ret = db_fetch_all($collection, _filter_fn)'
        with VM(self.unqlite, script) as vm:
            py_filter_fn = filter_fn
            filter_callback = py_filter_wrapper
            unqlite_create_function(
                vm.vm,
                '_filter_fn',
                filter_callback,
                NULL)
            vm['collection'] = self.name
            vm.execute()
            ret = vm['ret']
            unqlite_delete_function(
                vm.vm,
                '_filter_fn')

        return ret

    def create(self):
        """
        Create the named collection.

        Note: this does not create a new JSON document, this method is
        used to create the collection itself.
        """
        self._execute('if (!db_exists($collection)) {db_create($collection);}')

    def drop(self):
        """Drop the collection and all associated records."""
        self._execute('if (db_exists($collection)) { '
                      'db_drop_collection($collection); }')

    def exists(self):
        """Return boolean indicating whether the collection exists."""
        return self._simple_execute('$ret = db_exists($collection);')

    def last_record_id(self):
        """Return the ID of the last document to be stored."""
        return self._simple_execute('$ret = db_last_record_id($collection);')

    def current_record_id(self):
        """Return the ID of the current JSON document."""
        return self._simple_execute(
            '$ret = db_current_record_id($collection);')

    def reset_cursor(self):
        self._execute('db_reset_record_cursor($collection);')

    def __len__(self):
        """Return the number of records in the document collection."""
        return self._simple_execute('$ret = db_total_records($collection);')

    def delete(self, record_id):
        """Delete the document associated with the given ID."""
        script = '$ret = db_drop_record($collection, $record_id);'
        return self._simple_execute(script, record_id=record_id)

    def fetch(self, record_id):
        """Fetch the document associated with the given ID."""
        script = '$ret = db_fetch_by_id($collection, $record_id);'
        return self._simple_execute(script, record_id=record_id)

    def store(self, record, return_id=True):
        """
        Create a new JSON document in the collection, optionally returning
        the new record's ID.
        """
        if return_id:
            script = ('if (db_store($collection, $record)) { '
                      '$ret = db_last_record_id($collection); }')
        else:
            script = '$ret = db_store($collection, $record);'
        return self._simple_execute(script, record=record)

    def update(self, record_id, record):
        """
        Update the record identified by the given ID.
        """
        script = '$ret = db_update_record($collection, $record_id, $record);'
        return self._simple_execute(script, record_id=record_id, record=record)

    def fetch_current(self):
        return self._simple_execute('$ret = db_fetch($collection);')

    def __delitem__(self, record_id):
        self.delete(record_id)

    def __getitem__(self, record_id):
        return self.fetch(record_id)

    def error_log(self):
        return self._simple_execute('$ret = db_errlog();')


cdef unqlite_value_to_python(unqlite_value *ptr):
    cdef int nbytes
    cdef list json_array
    cdef dict json_object

    if unqlite_value_is_json_object(ptr):
        json_object = {}
        unqlite_array_walk(
            ptr,
            unqlite_value_to_dict,
            <void *>json_object)
        return json_object
    elif unqlite_value_is_json_array(ptr):
        json_array = []
        unqlite_array_walk(
            ptr,
            unqlite_value_to_list,
            <void *>json_array)
        return json_array
    elif unqlite_value_is_string(ptr):
        return str(unqlite_value_to_string(ptr, &nbytes))[:nbytes]
    elif unqlite_value_is_int(ptr):
        return unqlite_value_to_int(ptr)
    elif unqlite_value_is_float(ptr):
        return unqlite_value_to_double(ptr)
    elif unqlite_value_is_bool(ptr):
        return bool(unqlite_value_to_bool(ptr))
    elif unqlite_value_is_null(ptr):
        return None
    raise TypeError('Unrecognized type.')

cdef python_to_unqlite_value(VM vm, unqlite_value *ptr, python_value):
    cdef unqlite_value *item_ptr = <unqlite_value *>0

    if isinstance(python_value, unicode):
        unqlite_value_string(ptr, python_value.encode('utf-8'), -1)
    elif isinstance(python_value, basestring):
        unqlite_value_string(ptr, python_value, -1)
    elif isinstance(python_value, (list, tuple)):
        for item in python_value:
            item_ptr = vm.create_value(item)
            unqlite_array_add_elem(ptr, NULL, item_ptr)
            vm.release_value(item_ptr)
    elif isinstance(python_value, dict):
        for key, value in python_value.items():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            item_ptr = vm.create_value(value)
            unqlite_array_add_strkey_elem(
                ptr,
                key,
                item_ptr)
            vm.release_value(item_ptr)
    elif isinstance(python_value, (int, long)):
        unqlite_value_int(ptr, python_value)
    elif isinstance(python_value, bool):
        unqlite_value_bool(ptr, python_value)
    elif isinstance(python_value, float):
        unqlite_value_double(ptr, python_value)
    else:
        unqlite_value_null(ptr)

cdef int unqlite_value_to_list(unqlite_value *key, unqlite_value *value, void *user_data):
    cdef list accum
    accum = <list>user_data
    accum.append(unqlite_value_to_python(value))

cdef int unqlite_value_to_dict(unqlite_value *key, unqlite_value *value, void *user_data):
    cdef dict accum
    accum = <dict>user_data
    accum[unqlite_value_to_python(key)] = unqlite_value_to_python(value)
