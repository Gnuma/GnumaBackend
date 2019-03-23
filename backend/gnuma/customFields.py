from rest_framework import serializers    

class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import base64
        import io
        """
        Data is an instance of InMemoryUploadedFile class.
        """
        if isinstance(data, InMemoryUploadedFile):
            data_decoded = b''
            for byte in data.chunks():
                try:
                    data_decoded += base64.b64decode(byte, validate = True)
                except Exception as e:
                    print('EXCEPTION RAISED IN B64 DECODE: %s' % str(e))
            
        newFile = io.BytesIO(data_decoded)
        newData = InMemoryUploadedFile(file = newFile, name = data.name, size = data.size, content_type = data.content_type, content_type_extra = data.content_type_extra, charset = data.charset, field_name = data.field_name)
        #
        # Now we got our original data decoded, so just let's run the DRF's validating process.
        #
        return super(Base64ImageField, self).to_internal_value(newData)