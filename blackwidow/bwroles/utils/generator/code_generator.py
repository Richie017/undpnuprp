import os
__author__ = 'Sohel'

class BWCodeGenerator(object):

    @classmethod
    def generate_source_file(cls, file_path, file_name, content, **kwargs):
        try:
            file_path_abs = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            with open(file_path_abs, 'w+') as f:
                f.write(content)
            return file_path_abs
        except Exception as exp:
            print(exp)
            return False

    @classmethod
    def adjust_with_indent(cls, line, indent, depth):
        return line.rjust(len(line) + indent * depth)

    @classmethod
    def generate_python_modelmixin_class(cls, model_name, base_class_name, proxy=False, method_list=[], imports=[], indent=4, newline_sep='\n'):
        import_states = str("%s" % newline_sep).join(imports)

        mixin_class_name = model_name.strip().replace(' ','')+"ModelBase"

        class_code = """class %s(%s):""" % (mixin_class_name, base_class_name)
        class_code += newline_sep

        meta_depth = 1

        meta_class = cls.adjust_with_indent("class Meta:%s" % newline_sep, indent, meta_depth)

        meta_depth += 1

        if proxy:
            meta_class += cls.adjust_with_indent("proxy=True", indent, meta_depth)
        else:
            meta_class += cls.adjust_with_indent("pass", indent, meta_depth)

        class_code += meta_class

        source_code = import_states + newline_sep * 2 + "__author__='__auto_generated__'%s" % newline_sep + newline_sep * 2 + class_code
        return mixin_class_name, source_code

    @classmethod
    def generate_python_model_class(cls, class_name, parent_class_name, attrs=[], decorators=[], method_list=[],
                                    imports=[], proxy=False, indent=4, newline_sep='\n'):

        mixin_imports = []
        for index, item in enumerate(imports):
            if item.endswith(parent_class_name):
                mixin_imports += [ imports.pop(index) ]
                break

        mixin_class_name, mixin_source_code = cls.generate_python_modelmixin_class(class_name, parent_class_name, proxy=proxy, imports=mixin_imports)

        if decorators:
            imports.append('from blackwidow.engine.decorators.utility import decorate')
        import_states = str("%s" % newline_sep).join(imports)


        indent_depth = 0

        if decorators:
            decorator_str = '@decorate(' + ','.join(decorators) + ')' + newline_sep
        else:
            decorator_str = ''

        line = """class %s(%s):""" % ( class_name, mixin_class_name )
        line_with_indent = cls.adjust_with_indent(line, indent, indent_depth)

        class_code = decorator_str

        class_code += line_with_indent

        class_code += newline_sep

        indent_depth += 1

        attrs_str = str("%s" % newline_sep).join([cls.adjust_with_indent(l, indent, indent_depth) for l in attrs])

        class_code += attrs_str

        class_code += newline_sep

        meta_depth = 1

        meta_class = cls.adjust_with_indent("class Meta:%s" % newline_sep, indent, meta_depth)

        meta_depth += 1

        if proxy:
            meta_class += cls.adjust_with_indent("proxy=True", indent, meta_depth)
        else:
            meta_class += cls.adjust_with_indent("pass", indent, meta_depth)

        class_code += meta_class

        model_class_source_code = import_states + newline_sep * 2 + "__author__='__auto_generated__'%s" % newline_sep + newline_sep * 2 + class_code

        return mixin_source_code, model_class_source_code

    @classmethod
    def generate_python_formmixin_class(cls, model_name, base_form_name, method_list=[], imports=[], indent=4, newline_sep='\n'):
        import_states = str("%s" % newline_sep).join(imports)

        mixin_class_name = model_name.strip().replace(' ','')+"BaseForm"

        class_code = """class %s(%s):""" % (mixin_class_name, base_form_name )
        class_code += newline_sep
        indent_depth = 1

        init_indent_depth = 1

        init_method = cls.adjust_with_indent("def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):", indent, init_indent_depth)
        init_method += newline_sep

        init_indent_depth += 1

        init_method += cls.adjust_with_indent("super().__init__(data=data, files=files, instance=instance, **kwargs)", indent, init_indent_depth)

        init_method += newline_sep

        class_code += init_method

        source_code = import_states + newline_sep * 2 + "__author__='__auto_generated__'%s" % newline_sep + newline_sep * 2 + class_code
        return mixin_class_name, source_code

    @classmethod
    def generate_python_form_class(cls, form_class_name, parent_class_name, model_name, method_list=[],
                                   imports=[], indent=4, newline_sep='\n'):

        mixin_imports = []
        for index, item in enumerate(imports):
            if item.endswith(parent_class_name):
                mixin_imports += [ imports.pop(index) ]
                break

        mixin_class_name, mixin_source_code = cls.generate_python_formmixin_class(model_name, base_form_name=parent_class_name, imports=mixin_imports)

        import_states = str("%s" % newline_sep).join(imports)

        class_code = """class %s(%s):""" % (form_class_name, mixin_class_name)
        class_code += newline_sep
        indent_depth = 1

        meta_class_str = cls.adjust_with_indent('class Meta(%s.Meta):' % mixin_class_name, indent, indent_depth)
        meta_class_str += newline_sep
        indent_depth += 1
        meta_class_str += cls.adjust_with_indent('model = %s' % model_name, indent, indent_depth)
        meta_class_str += newline_sep
        class_code += meta_class_str

        form_class_source_code = import_states + newline_sep * 2 + "__author__='__auto_generated__'%s" % newline_sep + newline_sep * 2 + class_code
        return mixin_source_code, form_class_source_code
