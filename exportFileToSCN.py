bl_info = {
    "name": "scn File Exporter",
    "author": "Jakub Jurek",
    "version": (0,9),
    "blender": (2, 59, 0),
    "location": "File > Export",
    "description": "Exports file to .scn",
    "warning": "file have to have scnObjectPanel properties",
    "wiki_url": "https://github.com/jurek1029/BlenderPlugins",
    "category": "Import-Export",
}

import bpy
import bmesh
from bpy import context
import struct
import os

tex = ""
mat = ""

def writeUV(normal,uv,f,obj,bm,uv_layer,uv_tex):
    global mat
    global tex
    mask = 0
    if normal:
        mask += 1
    if uv:
        mask += 2
    if obj.FlatShader:
        mask += 4
    f.write(struct.pack('<ci',b'o',mask)) #o ocznacza nowy obiekt mask pierwszy bit to normalne 2 bit to uv
    f.write(struct.pack('<i',(len(obj.name)+1)))# plus koniec stringa
    for c in obj.name:
        f.write(struct.pack('<B',ord(c))) # dlugosc nazwy obiektu
    f.write(struct.pack('<B',0)) # koniec stringa w c++
    verOut = []
    uvOut = []
    nOut = []
    temp = []
    faceOut = []
    
    for v in bm.verts: # tworzy kopie vertexow ktore maja wiecej niz jedo UV
        for l in v.link_loops:
            tempUV = [l[uv_layer].uv.x, l[uv_layer].uv.y]
            if not (tempUV in temp):
                #f.write("v %f %f %f\n" % (v.co.x, v.co.y, v.co.z))
                verOut.append([v.co.x, v.co.y, v.co.z])
                uvOut.append([l[uv_layer].uv.x, l[uv_layer].uv.y])
                nOut.append([v.normal.x,v.normal.y,v.normal.z])
            temp.append([l[uv_layer].uv.x, l[uv_layer].uv.y]) 
        temp = []
    
    if not obj.FlatShader:    
        f.write(struct.pack('<cci',b'c',b'v',len(verOut))) # liczba vertexow do wczytania
        if normal:
            for v,uv,n in zip(verOut,uvOut,nOut):
                f.write(struct.pack('<ffffffff',v[1],v[2],-v[0],n[1],n[2],-n[0],uv[0],uv[1]))
        else:
             for v,uv in zip(verOut,uvOut):
                f.write(struct.pack('<fffff',v[1],v[2],-v[0],uv[0],uv[1]))
    
    
   # if normal:
#        f.write(struct.pack('cci',b'c',b'n',len(nOut))) # liczba normalnych do wczytania
#        for n in nOut:
#            #f.write("n %f %f %f\n" % (n[0],n[1],n[2]))   
#            f.write(struct.pack('fff',n[0],n[1],n[2]))
    
#    f.write(struct.pack('cci',b'c',b'u',len(uvOut)))# liczba uv do wczytania
#    for uv in uvOut:
        #f.write("u %f %f \n" % (uv[0],uv[1]))
#        f.write(struct.pack('ff',uv[0],uv[1]))
    
    temp2 = []
    for i,(v, uv) in enumerate(zip(verOut, uvOut)):
        temp2.append([v,uv])
    fa = []
    for face in bm.faces:
        tex = getattr(face[uv_tex].image, "name", "")
        if "." not in tex:
            tex = tex +"."+getattr(face[uv_tex].image, "file_format", "")
        mat = obj.material_slots[face.material_index].material
        #f.write("f")                
        for loop, vert in zip(face.loops, face.verts):               
            #f.write(" %d" % temp2.index([[obj.data.vertices[vert.index].co.x, obj.data.vertices[vert.index].co.y, obj.data.vertices[vert.index].co.z], [loop[uv_layer].uv.x, loop[uv_layer].uv.y]]))
            fa.append(temp2.index([[obj.data.vertices[vert.index].co.x, obj.data.vertices[vert.index].co.y, obj.data.vertices[vert.index].co.z], [loop[uv_layer].uv.x, loop[uv_layer].uv.y]]))
        #f.write("\n")
        faceOut.append(fa)
        fa = []
        
    if obj.FlatShader:
        flatVec = []
        flatNor = []
        flatUv = []
        tempNor = []        
        for fa in faceOut:
            flatVec.append(verOut[fa[0]])
            flatVec.append(verOut[fa[1]])
            flatVec.append(verOut[fa[2]])
            tempNor = calcNorm(verOut[fa[0]],verOut[fa[1]],verOut[fa[2]])
            flatNor.append(tempNor)
            flatNor.append(tempNor)
            flatNor.append(tempNor)
            flatUv.append(uvOut[fa[0]])
            flatUv.append(uvOut[fa[1]])
            flatUv.append(uvOut[fa[2]])
        f.write(struct.pack('<cci',b'c',b'v',len(faceOut)*3)) # liczba vertexow do wczytania
        if normal:
            for v,uv,n in zip(flatVec,flatUv,flatNor):
                f.write(struct.pack('<ffffffff',v[1],v[2],-v[0],n[1],n[2],-n[0],uv[0],uv[1]))
        else:
             for v,uv in zip(flatVec,flatUv):
                f.write(struct.pack('<fffff',v[1],v[2],-v[0],uv[0],uv[1]))
                
    if not obj.FlatShader:    
        f.write(struct.pack('<cci',b'c',b'f',len(faceOut)))# liczba facow do wczytania
        for fa in faceOut:
            f.write(struct.pack('<iii',fa[0],fa[1],fa[2]))
        

def writeNoUV(normal,uv,f,obj,bm):
    global mat
    mask = 0
    if normal:
        mask += 1
    if obj.FlatShader:
        mask += 4
    f.write(struct.pack('<ci',b'o',mask)) #o ocznacza nowy obiekt mask pierwszy bit to normalne 2 bit to uv
    f.write(struct.pack('<i',(len(obj.name)+1)))# plus koniec stringa
    for c in obj.name:
        f.write(struct.pack('<B',ord(c))) # dlugosc nazwy obiektu
    f.write(struct.pack('<B',0)) #koniec stringa w c++
    
    if not obj.FlatShader:
        f.write(struct.pack('<cci',b'c',b'v',len(bm.verts))) # liczba vertexow do wczytania
        if normal:
            for v in bm.verts:
    			#f.write("v %f %f %f\n" % (v.co.x, v.co.y, v.co.z))
                f.write(struct.pack('<ffffff',v.co.y, v.co.z, -v.co.x,v.normal.y,v.normal.z,-v.normal.x))
        else:
            for v in bm.verts:
    			#f.write("v %f %f %f\n" % (v.co.x, v.co.y, v.co.z))
                f.write(struct.pack('<fff',v.co.y, v.co.z, -v.co.x))    
              
        f.write(struct.pack('<cci',b'c',b'f',len(bm.faces)))# liczba facow do wczytania          
        for face in bm.faces:
            mat = obj.material_slots[face.material_index].material
    		#f.write("f %d %d %d\n" % (face.verts[0].index,face.verts[1].index,face.verts[2].index))
            f.write(struct.pack('<III',face.verts[0].index,face.verts[1].index,face.verts[2].index))
    else:
        flatVec = []
        flatNor = []
        tempNor = []  
        verOut = []
        for v in bm.verts:
            x = v.co.x
            y = v.co.y
            z = v.co.z
            verOut.append([x,y,z])                  
        for fa in bm.faces:
            flatVec.append(verOut[fa.verts[0].index])
            flatVec.append(verOut[fa.verts[1].index])
            flatVec.append(verOut[fa.verts[2].index])
            tempNor = calcNorm(verOut[fa.verts[0].index],verOut[fa.verts[1].index],verOut[fa.verts[2].index])
            flatNor.append(tempNor)
            flatNor.append(tempNor)
            flatNor.append(tempNor)
        f.write(struct.pack('<cci',b'c',b'v',len(bm.faces)*3)) # liczba vertexow do wczytania
        if normal:
            for v,n in zip(flatVec,flatNor):
    			#f.write("v %f %f %f\n" % (v.co.x, v.co.y, v.co.z))
                f.write(struct.pack('<ffffff',v[1],v[2],-v[0],n[1],n[2],-n[0]))
        else:
            for v in flatVec:
    			#f.write("v %f %f %f\n" % (v.co.x, v.co.y, v.co.z))
                f.write(struct.pack('<fff',v[1],v[2],-v[0]))    
        for face in bm.faces:
            mat = obj.material_slots[face.material_index].material
         


def calcNorm(v1,v2,v3):
    ab = [v2[0] - v1[0],v2[1] - v1[1],v2[2] - v1[2]]
    ac = [v3[0] - v1[0],v3[1] - v1[1],v3[2] - v1[2]]
    return [ab[1]*ac[2] - ab[2]*ac[1], ab[2]*ac[0] - ab[0]*ac[2], ab[0]*ac[1] - ab[1]*ac[0]]

def write_some_data(context, filepath, normal, uv):
    objs = context.scene.objects   
    
    print("running write_some_data...")
    #f = open(filepath, 'w', encoding='utf-8')
    f = open(filepath, 'wb')
    f.write(struct.pack('<ci',b'n',len(objs)))
    for obj in objs:
        if obj.type == "MESH":
            
            obj.update_from_editmode()
            me = obj.data
          #  mat = ""
          #  tex = ""
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            if uv:
                uv_layer = bm.loops.layers.uv.active
                if uv_layer is None:
                    writeNoUV(normal,uv,f,obj,bm);
                    print("No active UV map (uv)")
                    #raise Exception("No active UV map (uv)")
                else:
                    uv_tex = bm.faces.layers.tex.active
                    if uv_tex is None:
                        writeNoUV(normal,uv,f,obj,bm)
                        print("No active UV map (tex)")
                        #raise Exception("No active UV map (tex)")
                    else:
                         writeUV(normal,uv,f,obj,bm,uv_layer,uv_tex)
               
                    
            else:
                writeNoUV(normal,uv,f,obj,bm)
                
            if mat is not None:
                #f.write("m %f %f %f %f %f %f %f %f\n" % (mat.diffuse_color[0],mat.diffuse_color[1],mat.diffuse_color[2],mat.specular_color[0],mat.specular_color[1],mat.specular_color[2],mat.specular_intensity,mat.alpha) )#deffuse #specualr #shine #transparency
                f.write(struct.pack('<cffffffff',b'm',mat.diffuse_color[0],mat.diffuse_color[1],mat.diffuse_color[2],mat.specular_color[0],mat.specular_color[1],mat.specular_color[2],mat.specular_intensity,mat.alpha))
             
            if tex is not None and uv:
                #f.write("t %s\n" % tex)
                print(tex)
                f.write(struct.pack('<cci',b'c',b't',(len(tex)+1))) # dlugosc nazwy textury
                for c in tex:
                    f.write(struct.pack('<B',ord(c))) # nazwa textury
                f.write(struct.pack('<B',0)) # koniec stringa w c++
                
                temp = os.path.relpath(obj.TexturePath, obj.ProjectPath) # znajdywanie relatywnej scieżki 
                temp +="\\"
                if temp == ".":
                    f.write(struct.pack('<i',-1))
                else:
                    f.write(struct.pack('<i',(len(temp)+1))) # dlugosc relatywnej lokalizacji textury
                    for c in temp:
                        f.write(struct.pack('<B',ord(c))) # lokalizacja textury
                    f.write(struct.pack('<B',0)) # koniec stringa w c++
            
            
            if obj.FragmentShaderName:          
                f.write(struct.pack('<c',b's'))# inforamcjie o shaderch
                temp = os.path.relpath(obj.ShaderPath, obj.ProjectPath) # znajdywanie relatywnej scieżki
                temp +="\\"
                if temp == ".":
                    f.write(struct.pack('<i',-1))
                else:      
                    f.write(struct.pack('<i',(len(temp)+1))) # dlugosc lokalizacji shadereow
                    for c in temp:
                        f.write(struct.pack('<B',ord(c))) # lokalizacja shaderow
                    f.write(struct.pack('<B',0)) # koniec stringa w c++
                      
                f.write(struct.pack('<i',(len(obj.FragmentShaderName)+1))) # dlugosc fragment shadera
                for c in obj.FragmentShaderName:
                    f.write(struct.pack('<B',ord(c))) # nazwa fragmanet shadera
                f.write(struct.pack('<B',0)) # koniec stringa w c++
                
                f.write(struct.pack('<i',(len(obj.VertexShaderName)+1))) # dlugosc verttex shadera
                for c in obj.VertexShaderName:
                    f.write(struct.pack('<B',ord(c))) # nazwa vertex shadera
                f.write(struct.pack('<B',0)) # koniec stringa w c++
                
                
            #if mat.raytrace_mirror.use:
                ##f.write("s %f %f %f %f\n" % (mat.mirror_color[0],mat.mirror_color[1],mat.mirror_color[2],mat.raytrace_mirror.reflect_factor))         
                #f.write(struct.pack('<cffff',b's',mat.mirror_color[0],mat.mirror_color[1],mat.mirror_color[2],mat.raytrace_mirror.reflect_factor))
    
    #f.write(struct.pack('<ci',b'o',mask)) #o ocznacza nowy obiekt mask pierwszy bit to normalne 2 bit to uv
    #nam="end"
    #f.write(struct.pack('<i',(len(nam)+1)))# plus koniec stringa
    #for c in nam:
    #    f.write(struct.pack('<B',ord(c))) # dlugosc nazwy obiektu
    #f.write(struct.pack('<B',0)) # koniec stringa w c++    
   
    f.close()
    bm.free()
    del bm
    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export to .scn"

    # ExportHelper mixin class uses this
    filename_ext = ".scn"

    filter_glob = StringProperty(
            default="*.scn",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    normal = BoolProperty(
            name="Normals",
            description="Czy exportowac normalne",
            default=True,
            )
            
    uv = BoolProperty(
            name="UV",
            description="Czy exportowac UV",
            default=True,
            )
           

    #type = EnumProperty(
    #        name="Example Enum",
    #        description="Choose between two items",
    #        items=(('OPT_A', "First Option", "Description one"),
    #               ('OPT_B', "Second Option", "Description two")),
    #        default='OPT_A',
    #        )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.normal, self.uv)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="Export to .scn")


def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
