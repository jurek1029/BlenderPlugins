
bl_info = {
    "name": "scn Object Panel",
    "author": "Jakub Jurek",
    "version": (0,3),
    "blender": (2, 59, 0),
    "location": "Properties > Window > Object",
    "description": "Set information for scn file exporter",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/",
    "category": "Object",
}

import bpy
from bpy.props import StringProperty

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = ".scn File Data"
    bl_idname = "scnObjectPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        
        row = layout.row()
        row.prop(obj, "ProjectPath")
        
        row = layout.row()
        row.prop(obj, "FragmentShaderName")
        
        row = layout.row()
        row.prop(obj, "VertexShaderName")
        
        row = layout.row()
        row.prop(obj, "ShaderPath")
        
        row = layout.row()
        row.prop(obj, "TexturePath")

        #row = layout.row()
        #row.operator("mesh.primitive_cube_add")


def register():
    #bpy.types.Object.car_color = FloatVectorProperty(subtype='COLOR', size=3)
    bpy.types.Object.ProjectPath = StringProperty(subtype='FILE_PATH')
    bpy.types.Object.FragmentShaderName = StringProperty(subtype='FILE_NAME')
    bpy.types.Object.VertexShaderName = StringProperty(subtype='FILE_NAME')
    bpy.types.Object.ShaderPath = StringProperty(subtype='FILE_PATH')
    bpy.types.Object.TexturePath = StringProperty(subtype='FILE_PATH')

    
    bpy.utils.register_class(HelloWorldPanel)


def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)


if __name__ == "__main__":
    register()
