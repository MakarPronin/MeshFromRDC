##########################################################
#   Import CSV Mesh Addon
#
#   Description: Import points from a CSV file and create a mesh with connected faces.
#   Author: Makar Pronin, Jolly Joe
#   Version: 1.0.0
#   Blender: 4.2.0
#   Category: Import-Export
#
#   Usage Instructions:
#   - Enable the addon in Blender's preferences.
#   - Go to "File > Import > CSV Mesh" to access the importer.
#   - Click "Import CSV Mesh" to generate the mesh from the CSV file.
#   
#   Terms of Use:
#   - You are free to use and distribute this addon for both personal and commercial purposes,
#     provided that you credit the authors (Makar Pronin, Jolly Joe) by including this comment block.
#   - If you make significant modifications let me know also,
#   consider sharing your changes with the community.
#
#   - Originally created by Jolly Joe
#
#   Contact Jolly Joe:
#   - CodeWizardJolly@protonmail.com
#   Contact Makar Pronin:
#   - artificialworld747@gmail.com
#
##########################################################

import bpy
import csv
import bmesh
from bpy_extras.io_utils import ImportHelper

bl_info = {
    "name": "Import CSV Mesh",
    "author": "Makar Pronin, Jolly Joe",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "File > Import",
    "description": "Import points from a CSV file and create a mesh with connected faces.",
    "category": "Import-Export",
}

class CSVMeshImporterOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.csv"
    bl_label = "Import CSV Mesh"
    bl_description = "Import points from a CSV file and create a mesh with connected faces."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            with open(self.filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                # Game Headers to name the rows in the file for script
                headers = {
                    'SV_Position.x': 2,
                    'SV_Position.y': 3,
                    'SV_Position.z': 4,
                    'SV_Position.w': 5,
                }
                
                next(reader)
                
                vertices = []
                
                for row in reader:                 
                    x = float(row[headers['SV_Position.x']])/float(row[headers['SV_Position.w']])
                    y = float(row[headers['SV_Position.y']])/float(row[headers['SV_Position.w']])
                    z = float(row[headers['SV_Position.z']])/float(row[headers['SV_Position.w']])

                    vertices.append((x, y, z))
                            
                mesh = bpy.data.meshes.new("CSV_Mesh")
                bm = bmesh.new()
                
                for vertex in vertices:
                    bm.verts.new(vertex)
                # Connect the vertices based on the selected connection method
                bm.verts.ensure_lookup_table()
                corner_indices = list(range(0, len(vertices) - 1, 3))
                for i in corner_indices:
                    if i + 1 < len(vertices):
                        bm.faces.new((bm.verts[i], bm.verts[i + 1], bm.verts[i + 2]))

            # Update the BMesh and populate the mesh with BMesh data
            bm.to_mesh(mesh)
            bm.free()

            # Create a new object from the mesh
            obj = bpy.data.objects.new("", mesh)
            context.collection.objects.link(obj)
            # Select the newly created object
            bpy.context.view_layer.objects.active = obj
            # Set object origin and scale
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            # Adjust this line based on the property's actual name
            bpy.types.Scene.scale_factor = 1.0
            # Merge by distance
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.001)
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # If Clean up loose geometry option checked
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_loose()
            bpy.ops.mesh.delete(type='EDGE')
            bpy.ops.object.mode_set(mode='OBJECT')
            # Recalculate normals
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
                    
            # Set object origin and scale
            bpy.ops.object.location_clear(clear_delta=False)

            # Create a new material
            material = bpy.data.materials.new(name="Material")
            
            # Configure material properties
            material.diffuse_color = (0.8, 0.5, 0.8, 1.0)
            # Assign the material to the mesh
            mesh.materials.append(material)
            # Show CSV plot points in a text window
            bpy.ops.text.new()
            text = bpy.data.texts[-1]
                            
            # Write vertices to text
            text.write("Vertices:\n")
            for vertex in vertices:
                text.write("({}, {}, {})\n".format(vertex[0], vertex[1], vertex[2]))
            
            # END OF PROGRAM
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        self.report({'INFO'}, "Mesh imported successfully.")
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(CSVMeshImporterOperator.bl_idname, text="CSV Mesh (.csv)")

def register():
    bpy.utils.register_class(CSVMeshImporterOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(CSVMeshImporterOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
