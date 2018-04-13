"""
Interfaces for Pypeline modules.
"""

import os
import sys
import warnings

from abc import abstractmethod, ABCMeta

import numpy as np

from PynPoint.Core.DataIO import OutputPort, InputPort, ConfigPort
from PynPoint.Util.Multiprocessing import LineProcessingCapsule, apply_function
from PynPoint.Util.ModuleTools import progress, memory_frames


class PypelineModule:
    """
    Abstract interface for the PypelineModule:

        * Reading Module (:class:`PynPoint.core.Processing.ReadingModule`)
        * Writing Module (:class:`PynPoint.core.Processing.WritingModule`)
        * Processing Module (:class:`PynPoint.core.Processing.ProcessingModule`)

    Each PypelinModule has a name as a unique identifier in the Pypeline and has to implement the
    functions *connect_database* and *run* which are used in the Pypeline methods.
    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 name_in):
        """
        Abstract constructor of a PypelineModule which needs a name as identifier.

        :param name_in: The name of the PypelineModule.
        :type name_in: str

        :return: None
        """

        assert (isinstance(name_in, str)), "Error: Name of the PypelineModule needs to be a string."

        self._m_name = name_in
        self._m_data_base = None
        self._m_config_port = ConfigPort("config")

    @property
    def name(self):
        """
        Returns the name of the PypelineModule. This property makes sure that the internal module
        name can not be changed.

        :return: The name of the PypelineModule/
        :rtype: str
        """

        return self._m_name

    @abstractmethod
    def connect_database(self,
                         database):
        """
        Abstract interface for the function *connect_database* which is needed to connect the Ports
        of a PypelineModule with the DataStorage.

        :param database: The DataStorage
        :type database: DataStorage
        """

        pass

    @abstractmethod
    def run(self):
        """
        Abstract interface for the run method of a PypelineModule which inheres the actual
        algorithm behind the module.
        """

        pass


class WritingModule(PypelineModule):
    """
    The abstract class WritingModule is an interface for processing steps in the pipeline which
    do not change the content of the internal DataStorage. They only have reading access to the
    central data base. WritingModules can be used to export data from the HDF5 database.
    WritingModules know the directory on the hard drive where the output of the module can be
    saved. If no output directory is given the default Pypeline output directory is used.
    WritingModules have a dictionary of input ports (self._m_input_ports) but no output ports.
    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 name_in,
                 output_dir=None):
        """
        Abstract constructor of a WritingModule which needs the unique name identifier as input
        (more information: :class:`PynPoint.core.Processing.PypelineModule`). In addition one can
        specify a output directory where the module will save its results. If no output directory is
        given the Pypeline default directory is used. This function is called in all *__init__()*
        functions inheriting from this class.

        :param name_in: The name of the WritingModule.
        :type name_in: str
        :param output_dir: Directory where the results will be saved.
        :type output_dir: str

        :return: None
        """

        super(WritingModule, self).__init__(name_in)

        assert (os.path.isdir(str(output_dir)) or output_dir is None), 'Error: Output directory ' \
            'for writing module does not exist - input requested: %s' % output_dir

        self.m_output_location = output_dir
        self._m_input_ports = {}

    def add_input_port(self,
                       tag):
        """
        Function which creates a new InputPort and appends it to the internal InputPort dictionary.
        This function should be used by classes inheriting from WritingModule to make sure that
        only InputPorts with unique tags are added. The new port can be used as: ::

             Port = self._m_input_ports[tag]

        or by using the returned Port.

        :param tag: Tag of the new input port.
        :type tag: str

        :return: The new InputPort.
        :rtype: InputPort
        """

        tmp_port = InputPort(tag)

        if self._m_data_base is not None:
            tmp_port.set_database_connection(self._m_data_base)

        self._m_input_ports[tag] = tmp_port

        return tmp_port

    def connect_database(self,
                         database):
        """
        Connects all ports in the internal input and output port dictionaries to the given database.
        This function is called by Pypeline and connects its DataStorage object to all module ports.

        :param data_base_in: The input database
        :type data_base_in: DataStorage

        :return: None
        """

        for port in self._m_input_ports.itervalues():
            port.set_database_connection(database)

        self._m_config_port.set_database_connection(database)

        self._m_data_base = database

    def get_all_input_tags(self):
        """
        Returns a list of all input tags to the WritingModule.

        :return: list of input tags
        :rtype: list
        """

        return self._m_input_ports.keys()

    @abstractmethod
    def run(self):
        pass


class ProcessingModule(PypelineModule):
    """
    The abstract class ProcessingModule is an interface for all processing steps in the pipeline
    which reads, processes and saves data. Hence they have reading and writing access to the central
    data base using a dictionary of output ports (self._m_output_ports) and a dictionary of input
    ports (self._m_input_ports).
    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 name_in):
        """
        Abstract constructor of a ProcessingModule which needs the unique name identifier as input
        (more information: :class:`PynPoint.core.Processing.PypelineModule`). Call this function in
        all __init__() functions inheriting from this class.

        :param name_in: The name of the Processing Module
        :type name_in: str
        """

        super(ProcessingModule, self).__init__(name_in)

        self._m_input_ports = {}
        self._m_output_ports = {}

    def add_input_port(self,
                       tag):
        """
        Method which creates a new InputPort and appends it to the internal InputPort dictionary.
        This function should be used by classes inheriting from WritingModule to make sure that
        only InputPorts with unique tags are added. The new port can be used as: ::

             Port = self._m_input_ports[tag]

        or by using the returned Port.

        :param tag: Tag of the new input port.
        :type tag: str

        :return: The new InputPort.
        :rtype: InputPort
        """

        tmp_port = InputPort(tag)

        if self._m_data_base is not None:
            tmp_port.set_database_connection(self._m_data_base)

        self._m_input_ports[tag] = tmp_port

        return tmp_port

    def add_output_port(self,
                        tag,
                        activation=True):
        """
        Method which creates a new OutputPort and append it to the internal OutputPort dictionary.
        This function should be used by classes inheriting from Processing Module to make sure that
        only OutputPorts with unique tags are added. The new port can be used as: ::

             Port = self._m_output_ports[tag]

        or by using the returned Port.

        :param tag: Tag of the new output port.
        :type tag: str
        :param activation: Activation status of the Port after creation. Deactivated Ports
                           will not save their results until the are activated.
        :type activation: bool

        :return: The new OutputPort.
        :rtype: OutputPort
        """

        tmp_port = OutputPort(tag, activate_init=activation)

        if tag in self._m_output_ports:
            warnings.warn("Tag '"+tag+"' already used. Updating...")

        if self._m_data_base is not None:
            tmp_port.set_database_connection(self._m_data_base)

        self._m_output_ports[tag] = tmp_port

        return tmp_port

    def connect_database(self,
                         database):
        """
        Connects all ports in the internal input and output port dictionaries to the database. This
        function is called by the Pypeline and connects its DataStorage object to all module ports.

        :param database: The input database
        :type database: DataStorage

        :return: None
        """

        for port in self._m_input_ports.itervalues():
            port.set_database_connection(database)

        for port in self._m_output_ports.itervalues():
            port.set_database_connection(database)

        self._m_config_port.set_database_connection(database)

        self._m_data_base = database

    def apply_function_in_time(self,
                               func,
                               image_in_port,
                               image_out_port,
                               func_args=None):
        """
        Applies a function to all lines in time.

        :param func: The input function.
        :type func: function
        :param image_in_port: InputPort which is linked to the input data.
        :type image_in_port: InputPort
        :param image_out_port: OutputPort which is linked to the result place.
        :type image_out_port: OutputPort
        :param func_args: Additional arguments which are needed by the function *func*.
        :type func_args: tuple

        :return: None
        """

        init_line = image_in_port[:, 0, 0]

        size = apply_function(init_line, func, func_args).shape[0]

        if image_out_port.tag == image_in_port.tag and size != image_in_port.get_shape()[0]:
            raise ValueError("Input and output port have the same tag while %s is changing " \
                "the length of the signal. Use different input and output ports instead." % func)

        image_out_port.set_all(np.zeros((size,
                                         image_in_port.get_shape()[1],
                                         image_in_port.get_shape()[2])),
                               data_dim=3,
                               keep_attributes=False)

        cpu = self._m_config_port.get_attribute("CPU")

        line_processor = LineProcessingCapsule(image_in_port,
                                               image_out_port,
                                               cpu,
                                               func,
                                               func_args,
                                               size)

        line_processor.run()

    def apply_function_to_images(self,
                                 func,
                                 image_in_port,
                                 image_out_port,
                                 message,
                                 func_args=None,):
        """
        Function which applies a specified function to all images of a 3D data stack. The function
        requires an InputPort, and OutputPort, and a function with its arguments. Since the input
        dataset might be larger than the available memory, the MEMORY attribute from the central
        configuration is used to load images into the memory. Note that the function *func* is not
        allowed to change the shape of the images if the input and output port have the same tag
        MEMORY is not None.

        :param func: The function which is applied to all images. Its definitions should be
                     similar to: ::

                         def function(image_in,
                                      parameter1,
                                      parameter2,
                                      parameter3)

        :type func: function
        :param image_in_port: InputPort which is linked to the input data.
        :type image_in_port: InputPort
        :param image_out_port: OutputPort which is linked to the result place. No data is written
                               if set to None.
        :type image_out_port: OutputPort
        :param message: Progress message for the standard output.
        :type message: str
        :param func_args: Additional arguments which are needed by the function *func*.
        :type func_args: tuple

        :return: None
        """

        memory = self._m_config_port.get_attribute("MEMORY")

        ndim = image_in_port.get_ndim()

        if ndim == 2:
            nimages = 1
        elif ndim == 3:
            nimages = image_in_port.get_shape()[0]

        if image_out_port is not None and image_out_port.tag != image_in_port.tag:
            image_out_port.del_all_attributes()
            image_out_port.del_all_data()

        frames = memory_frames(memory, nimages)

        for i, _ in enumerate(frames[:-1]):
            progress(i, len(frames[:-1]), message)

            if ndim == 2:
                images = image_in_port[:, :]
            elif ndim == 3:
                images = image_in_port[frames[i]:frames[i+1], ]

            result = []

            if func_args is None:
                if ndim == 2:
                    result.append(func(images))

                elif ndim == 3:
                    for k in range(images.shape[0]):
                        result.append(func(images[k]))

            else:
                if ndim == 2:
                    result.append(func(images, * func_args))

                elif ndim == 3:
                    for k in range(images.shape[0]):
                        result.append(func(images[k], * func_args))

            if image_out_port is not None:
                if image_out_port.tag == image_in_port.tag:
                    try:
                        if np.size(frames) == 2:
                            image_out_port.set_all(np.asarray(result), keep_attributes=True)

                        else:
                            image_out_port[frames[i]:frames[i+1]] = np.asarray(result)

                    except TypeError:
                        raise ValueError("Input and output port have the same tag while %s is "
                                         "changing the image shape. This is only possible with "
                                         "MEMORY=None." % func)

                else:
                    image_out_port.append(np.asarray(result))

        sys.stdout.write(message+" [DONE]\n")
        sys.stdout.flush()

    def get_all_input_tags(self):
        """
        Returns a list of all input tags to the ProcessingModule.

        :return: List of input tags.
        :rtype: list(str)
        """

        return self._m_input_ports.keys()

    def get_all_output_tags(self):
        """
        Returns a list of all output tags to the ProcessingModule.

        :return: List of output tags.
        :rtype: list(str)
        """

        return self._m_output_ports.keys()

    @abstractmethod
    def run(self):
        pass


class ReadingModule(PypelineModule):
    """
    The abstract class ReadingModule is an interface for processing steps in the Pypeline which
    have only read access to the central data storage. One can specify a directory on the hard
    drive where the input data for the module is located. If no input directory is givennthe
    default Pypeline input directory is used. Reading modules have a dictionary of output ports
    (self._m_out_ports) but no input ports.
    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 name_in,
                 input_dir=None):
        """
        Abstract constructor of ReadingModule which needs the unique name identifier as input
        (more information: :class:`PynPoint.core.Processing.PypelineModule`). An input directory
        can be specified for the location of the data or else the Pypeline default directory is
        used. This function is called in all *__init__()* functions inheriting from this class.

        :param name_in: The name of the ReadingModule.
        :type name_in: str
        :param input_dir: Directory where the input files are located.
        :type input_dir: str

        :return: None
        """

        super(ReadingModule, self).__init__(name_in)

        assert (os.path.isdir(str(input_dir)) or input_dir is None), 'Error: Input directory ' \
            'for reading module does not exist - input requested: %s' % input_dir

        self.m_input_location = input_dir
        self._m_output_ports = {}

    def add_output_port(self,
                        tag,
                        activation=True):
        """
        Method which creates an OutputPort and appends it to the internal OutputPort dictionary.
        This function should be used by classes inheriting from ReadingModule to make sure that
        only OutputPorts with unique tags are added. The new port can be used as: ::

             Port = self._m_output_ports[tag]

        or by using the returned Port.

        :param tag: Tag of the new OutputPort.
        :type tag: str
        :param activation: Activation status of the Port after creation. Deactivated Ports
                           will not save their results until the are activated.
        :type activation: bool

        :return: The new OutputPort.
        :rtype: OutputPort
        """

        tmp_port = OutputPort(tag, activate_init=activation)

        if tag in self._m_output_ports:
            warnings.warn("Tag '"+tag+"' already used. Updating...")

        if self._m_data_base is not None:
            tmp_port.set_database_connection(self._m_data_base)

        self._m_output_ports[tag] = tmp_port

        return tmp_port

    def connect_database(self,
                         database):
        """
        Connects all ports in the internal input and output port dictionaries to the given database.
        This function is called by Pypeline and connects the DataStorage object to all module ports.

        :param database: The input database.
        :type database: DataStorage

        :return: None
        """

        for port in self._m_output_ports.itervalues():
            port.set_database_connection(database)

        self._m_config_port.set_database_connection(database)

        self._m_data_base = database

    def get_all_output_tags(self):
        """
        Returns a list of all output tags to the ReadingModule.

        :return: List of output tags.
        :rtype: list, str
        """

        return self._m_output_ports.keys()

    @abstractmethod
    def run(self):
        pass
