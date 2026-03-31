# -*- coding: utf-8 -*-
"""
Utility functions for Aspen Plus COM interface.
Handles unit listing, finding, conversion, and decorators.

Corresponds to: mcp_tools/utils/
"""

from functools import wraps
import UserDifineException as UDE


class UtilsMixin:
    """Mixin class for Aspen Plus utility functions."""

    def UnitList(self, item=None, table=False):
        """Show the Unit Table or specified category or specified unit in AspenPlus.

        :param item: if [], list the supported Unit category in AspenPlus.
                    if [integer], list the supported Unit in specified Unit category in AspenPlus.
                    if [integer, integer], show the Unit for specified parameters.
        :param table: a boolen value. default is False for print the result on the screen. 
                     If table=True, return result in dictionary type.
        """
        if (type(item) != list) and (item is not None):
            raise TypeError("item has to be a 'None' or "
                            + "'List' with 1 integer parameter or "
                            + "'List' with 2 integer parameters!!")
        if type(table) != bool:
            raise TypeError("table must be 'Boolen' value.")

        # List unit categories
        if item is None:
            UT = {}
            for index, e in enumerate(self.aspen.Tree.Elements("Unit Table").Elements, start=1):
                if table:
                    UT[index] = e.Name
                elif not table:
                    print("{0:3d}{1:>15s}".format(index, e.Name))
        # List units in selected category
        elif (type(item[0]) is int) and (len(item) == 1):
            if item[0] > len(self.aspen.Tree.Elements("Unit Table").Elements):
                raise IndexError('The 1st index is out of range.')

            UT = {}
            ename = self.aspen.Tree.Elements("Unit Table").Elements.Item(item[0] - 1).Name
            for index, e in enumerate(self.aspen.Tree.Elements("Unit Table").Elements(ename).Elements, start=1):
                if table:
                    UT[index] = e.Name
                elif not table:
                    print("{0:3d}{1:>15s}".format(index, e.Name))
        # Show unit for two integer parameters
        elif (type(item[0]) is int) and (type(item[1]) is int) and (len(item) == 2):
            if item[1] > len(self.aspen.Tree.Elements("Unit Table").Elements.Item(item[0] - 1).Elements):
                raise IndexError('The 2nd index is out of range.')

            ename = self.aspen.Tree.Elements("Unit Table").Elements.Item(item[0] - 1).Elements.Item(item[1] - 1).Name
            if table:
                UT = ename
            elif not table:
                print(ename)
        else:
            raise TypeError("item has to be a 'None' or "
                            + "'List' with 1 integer parameter or "
                            + "'List' with 2 integer parameters!!")

        if table:
            return UT
        elif not table:
            return

    def UnitFind(self, obj, table=False):
        """Get the unit of physics property in AspenFile for the current unit setting.

        :param obj: an Aspen COMObject for the physics properties.
        :param table: a boolen value. default is False for print the result on the screen.
        :return: If table=True, return result in string.
        """
        if type(table) != bool:
            raise TypeError("table must be 'Boolen' value.")

        pq = obj.AttributeValue(2)
        um = obj.AttributeValue(3)
        return self.UnitList([pq, um], table=table)

    def UnitChange(self, obj, unit_index):
        """Change the Unit in AspenFile for the physics properties.

        :param obj: an Aspen COMObject for the physics property.
        :param unit_index: index for the specified physics property in AspenPlus.
        :return: float. a value with changing unit.
        """
        pq = obj.AttributeValue(2)
        um = unit_index

        if type(um) != int:
            raise TypeError("unit_index must be integer")
        if type(pq) != int:
            raise IOError("obj doesn't has the unit. "
                          + "Please Check the input of obj.")

        if um > len(self.aspen.Tree.Elements("Unit Table").Elements.Item(pq - 1).Elements):
            raise IndexError('The um index is out of range.')

        return obj.ValueForUnit(pq, um)


# ========== Decorators ==========

def check_name(Type):
    """Check the input variable-type for the name is correct or not.
    Also checks whether the name is in the file or not.
    Finally, return the upper name to the program.
    
    Available name-type: block, stream.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            def name_up_and_arg_change(name, args):
                """Convert name to uppercase and update args."""
                name = name.upper()
                args = list(args)
                args[0] = name
                args = tuple(args)
                return name, args

            if Type == 'stream':
                sname = args[0]

                if type(sname) != str:
                    raise TypeError("sname must be a 'String'.")

                sname, args = name_up_and_arg_change(sname, args)

                if sname not in self.master.StreamsNameList():
                    raise ValueError("sname is not in the file. "
                                     + "Please Check the name you type.")
            elif Type == 'block':
                bname = args[0]

                if type(bname) != str:
                    raise TypeError("bname must be a 'String'.")

                bname, args = name_up_and_arg_change(bname, args)

                if bname not in self.master.BlocksNameList():
                    raise ValueError("bname is not in the file. "
                                     + "Please Check the name you type.")
            else:
                raise TypeError('No Match Value for Type, '
                                + 'Please Check the value you type.')

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
