import paddle.v2.framework.core as core
import unittest
import numpy
import paddle.v2.framework.create_op_creation_methods as creation


class OpTestMeta(type):
    def __new__(cls, name, bases, attrs):
        obj = super(OpTestMeta, cls).__new__(cls, name, bases, attrs)

        def test_all(self):
            func = getattr(creation.op_creations, self.type, None)
            self.assertIsNotNone(func)

            scope = core.Scope(None)
            kwargs = dict()

            for in_name in func.all_input_args:
                if hasattr(self, in_name):
                    kwargs[in_name] = in_name
                    var = scope.create_var(in_name).get_tensor()
                    arr = getattr(self, in_name)
                    var.set_dims(arr.shape)
                    var.set(arr)
                else:
                    kwargs[in_name] = "@EMPTY@"

            for out_name in func.all_output_args:
                if hasattr(self, out_name):
                    kwargs[out_name] = out_name
                    scope.create_var(out_name).get_tensor()

            for attr_name in func.all_attr_args:
                if hasattr(self, attr_name):
                    kwargs[attr_name] = getattr(self, attr_name)

            op = func(**kwargs)

            op.infer_shape(scope)

            ctx = core.DeviceContext.cpu_context()
            op.run(scope, ctx)

            for out_name in func.all_output_args:
                actual = numpy.array(scope.get_var(out_name).get_tensor())
                expect = getattr(self, out_name)
                numpy.testing.assert_almost_equal(actual, expect)

        obj.test_all = test_all
        return obj
