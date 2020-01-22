import launch

class LaunchType(object):
    __value__ = None
    __c_instance__ = None

    def __init__(self, value, allocator):
        self.__value__ = value
        self.__c_instance__ = allocator(value)
        if self.__c_instance__ == None:
            raise ValueError("Unable to create a LaunchType object.")
    
    def __repr__(self):
        return str(self.__value__)
    
    def __del__(self):
        if self.__c_instance__:
            launch.launch_data_free(self.__c_instance__)

    def getCPtr(self):
        return self.__c_instance__

    def getValue(self):
        return self.__value__

class LaunchInteger(LaunchType):
    def __init__(self, value):
        if type(value) is not int:
            raise TypeError("LaunchInteger expects int type.")
        super().__init__(value, launch.launch_data_new_integer)

class LaunchFD(LaunchType):
    def __init__(self, value):
        if type(value) is not int or value < 0:
            raise TypeError("LaunchFD expects unsigned int type.")
        super().__init__(value, launch.launch_data_new_fd)

class LaunchMachport(LaunchType):
    def __init__(self, value):
        if type(value) is not int or value < 0:
            raise TypeError("LaunchMachport expects unsigned int type.")
        super().__init__(value, launch.launch_data_new_machport)

class LaunchReal(LaunchType):
    def __init__(self, value):
        if type(value) is not float:
            raise TypeError("LaunchReal expects float type.")
        super().__init__(value, launch.launch_data_new_real)

class LaunchBool(LaunchType):
    def __init__(self, value):
        if type(value) is not bool:
            raise TypeError("LaunchBool expects bool type.")
        super().__init__(value, launch.launch_data_new_bool)

class LaunchString(LaunchType):
    def __init__(self, value):
        if type(value) is not str:
            raise TypeError("LaunchString expects str type.")
        self.__value__ = value
        self.__cvalue__ = value.encode('utf-8"')
        self.__c_instance__ = launch.launch_data_new_string(value.encode("utf-8"))
    
    def getCStr(self):
        return self.__cvalue__

class LaunchErrno(LaunchType):
    def __init__(self, value):
        self.__value__ = value

class LaunchDictionary(LaunchType):
    def __init__(self, dictionary = {}):

        if type(dictionary) is not dict:
            raise TypeError("LaunchDictionary expects dict type.")

        self.__value__ = {}
        self.__c_instance__ = launch.launch_data_alloc(launch.LAUNCH_DATA_DICTIONARY)
        if self.__c_instance__ == None:
            raise ValueError("Unable to create a LaunchDictionary object.")

        for key in dictionary:
            value = dictionary[key]
            self.insert(key, value)

    def insert(self, key, value):
        if (type(key) is not str) and (type(key) is not LaunchString):
            raise KeyError("LaunchDictionary expects str or LaunchString types as keyes.")

        if type(key) is str: key = LaunchString(key)
        if type(value) is str: value = LaunchString(value)
        elif type(value) is int: value = LaunchInteger(value)
        elif type(value) is bool: value = LaunchBool(value)
        elif type(value) is float: value = LaunchReal(value)
        elif type(value) is dict: value = LaunchDictionary(value)
        elif type(value) is list: value = LaunchArray(value)

        if not isinstance(value, LaunchType):
            raise TypeError("LaunchDictionary expects a primary type or LaunchType instances as values.")

        self.__value__[key.getValue()] = value
        ret = launch.launch_data_dict_insert(self.__c_instance__, value.getCPtr(), key.getCStr())
        if ret == False:
            raise ValueError("Unable to insert a value into a LaunchDictionary object.")
        
    def find(self, key):
        if (type(key) is not str) and (type(key) is not LaunchString):
            raise KeyError("LaunchDictionary expects str or LaunchString types as keyes.")

        if type(key) is LaunchString:
            key = key.getValue()

        return self.__value__[key]

    def remove(self, key):
        if (type(key) is not str) and (type(key) is not LaunchString):
            raise KeyError("LaunchDictionary expects str or LaunchString types as keyes.")
        
        if type(key) is str: key = LaunchString(key)
        if launch.launch_data_dict_remove(self.__c_instance__, key.getCStr()) == True:
            del self.__value__[key.getValue()]
            return True
        return False

    def __len__(self):
        return len(self.__value__)

    def __del__(self):
        if self.__c_instance__:
            launch.launch_data_free(self.__c_instance__)
        
        #children are freed by parent
        for entry in self.__value__:
            entry = self.__value__[entry]
            entry.__c_instance__ = None

class LaunchArray(LaunchType):
    def __init__(self, array = []):
        if type(array) is not list:
            raise TypeError("LaunchArray expects list type.")
        
        self.__value__ = []
        self.__c_instance__ = launch.launch_data_alloc(launch.LAUNCH_DATA_ARRAY)
        if self.__c_instance__ == None:
            raise ValueError("Unable to create a LaunchArray object.")
        length = len(array)
        for i in range(0, length):
            self.append(array[i])

    def setValueAt(self, index, value):
        if (type(index) is not int) and (type(index) is not LaunchInteger):
            raise KeyError("LaunchArray expects int or LaunchInteger types as indices.")

        if type(index) is int: index = LaunchInteger(index)
        if type(value) is str: value = LaunchString(value)
        elif type(value) is int: value = LaunchInteger(value)
        elif type(value) is bool: value = LaunchBool(value)
        elif type(value) is float: value = LaunchReal(value)
        elif type(value) is dict: value = LaunchDictionary(value)
        elif type(value) is list: value = LaunchArray(value)

        if not isinstance(value, LaunchType):
            raise TypeError("LaunchArray expects a primary type or LaunchType instances as values.")

        if index.getValue() < 0 or index.getValue() > len(self.__value__):
            raise IndexError("index out of bound of a LaunchArray object.")

        if index.getValue() == len(self.__value__):
             self.__value__.append(value)
        else:
            self.__value__[index.getValue()] = value

        ret = launch.launch_data_array_set_index(self.__c_instance__, value.getCPtr(), index.getValue())
        if ret == False:
            raise ValueError("Unable to insert a value into a LaunchArray object.")

    def getValueAt(self, index):
        if (type(index) is not int) and (type(index) is not LaunchInteger):
            raise KeyError("LaunchArray expects int or LaunchInteger types as indices.")

        if type(index) is LaunchInteger:
            index = index.getValue()

        return self.__value__[index]
    
    def append(self, value):
        self.setValueAt(len(self.__value__), value)

    def __len__(self):
        return len(self.__value__)

    def __del__(self):
        if self.__c_instance__:
            launch.launch_data_free(self.__c_instance__)
        
        #children are freed by parent
        for entry in self.__value__:
                entry.__c_instance__ = None

class LaunchDecoder():
    __decoded__ = None
    def __init__(self, data):
        data_type = launch.launch_data_get_type(data)
        if data_type == launch.LAUNCH_DATA_INTEGER:
            self.__decoded__ = LaunchInteger(launch.launch_data_get_integer(data))
        elif data_type == launch.LAUNCH_DATA_BOOL:
            self.__decoded__ = LaunchBool(launch.launch_data_get_bool(data))
        elif data_type == launch.LAUNCH_DATA_STRING:
            string = launch.launch_data_get_string(data).decode("utf-8")
            self.__decoded__ = LaunchString(string)
        elif data_type == launch.LAUNCH_DATA_MACHPORT:
            self.__decoded__ = LaunchMachport(launch.launch_data_get_machport(data))
        elif data_type == launch.LAUNCH_DATA_DICTIONARY:
            self.__decoded__ = {}
            launch.launch_data_dict_iterate(data, launch.launch_data_dict_iterator_t(self.__dictionary_iterator_callback__), 0)
        elif data_type == launch.LAUNCH_DATA_ARRAY:
            self.__decoded__ = []
            count = launch.launch_data_array_get_count(data)
            for i in range(0, count):
                result = launch.launch_data_array_get_index(data, i)
                self.__decoded__.append(LaunchDecoder(result).getValue())
        elif data_type == launch.LAUNCH_DATA_FD:
            self.__decoded__ = LaunchFD(launch.launch_data_get_fd(data))
        elif data_type == launch.LAUNCH_DATA_REAL:
            self.__decoded__ = LaunchReal(launch.launch_data_get_real(data))
        elif data_type == launch.LAUNCH_DATA_ERRNO:
            self.__decoded__ = LaunchErrno(launch.launch_data_get_errno(data))
        else:
            self.__decoded__ = LaunchString("?")
        
        if isinstance(self.__decoded__, LaunchType):
            self.__decoded__ = self.__decoded__.getValue()

    def __dictionary_iterator_callback__(self, value, key, ctx):     
        self.__decoded__[key.decode("utf-8")] = LaunchDecoder(value).getValue()

    def getValue(self):
        return self.__decoded__

    def __repr__(self):
        return str(self.__decoded__)

def launchMsg(msg):

    if type(msg) is str: msg = LaunchString(msg)
    elif type(msg) is int: msg = LaunchInteger(msg)
    elif type(msg) is bool: msg = LaunchBool(msg)
    elif type(msg) is float: msg = LaunchReal(msg)
    elif type(msg) is dict: msg = LaunchDictionary(msg)
    elif type(msg) is list: msg = LaunchArray(msg)

    if not isinstance(msg, LaunchType):
        raise TypeError("launchMsg expects a primary type or LaunchType instances as argument.")

    res = launch.launch_msg(msg.getCPtr())
    if res == None:
        raise ValueError("An error occured. Errors are not handled yet")
        import sys
        sys.exit(1)

    decoded = LaunchDecoder(res)
    launch.launch_data_free(res)
    return decoded.getValue()

