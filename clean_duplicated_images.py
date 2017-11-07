import bpy

bl_info = {
    "name": "Clean duplicated images",
    "description": "Single Line Explanation",
    "author": "Legigan Jeremy AKA Pistiwique from a Vinc3r idea",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Object"}

imageToClean = []
textureToClean = []


def get_original_images(image):
    if not "." in image.name:
        return image

    base, extension = image.name.rsplit(".", 1)

    if not extension.isdigit():
        return image

    listIndex = {'index': [], 'imgData': []}

    for name, imgData in bpy.data.images.items():
        if name == base:
            return imgData
        if base in name:
            listIndex['index'].append(int(name.split(".")[-1]))
            listIndex['imgData'].append(imgData)

    minIndex = min(listIndex['index'])

    idx = listIndex['index'].index(minIndex)

    return listIndex['imgData'][idx]


def cycles_assignment(material):
    imageToClean = []
    for node in material.material.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            image = get_original_images(node.image)
            if image != node.image:
                imageToClean.append(node.image)
                node.image = image


def get_texture(image):
    for tex in bpy.data.textures:
        if tex.image == image:
            return tex


def internal_assignment(obj, mat):
    for idx, slot in enumerate(mat.material.texture_slots):
        if slot:
            image = get_original_images(slot.texture.image)
            if image != slot.texture.image:
                imageToClean.append(slot.texture.image)
                textureToClean.append(slot.texture)
                slot.texture.image = image
                texture = get_texture(image)
                slot.texture = texture
                OBJ = bpy.context.active_object
                MODE = bpy.context.object.mode
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
                bpy.ops.object.mode_set(mode=MODE)
                bpy.context.scene.objects.active = OBJ


class CleanDuplicated(bpy.types.Operator):
    bl_idname = "image.clean_duplicated"
    bl_label = "Clean Duplicated"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        for obj in bpy.context.scene.objects:
            if obj.material_slots:
                for mat in obj.material_slots:
                    if bpy.context.scene.render.engine == 'CYCLES':
                        cycles_assignment(mat)
                    elif bpy.context.scene.render.engine == 'BLENDER_RENDER':
                        internal_assignment(obj, mat)

        for img in imageToClean:
            bpy.data.images.remove(img, do_unlink=True)

        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            for tex in textureToClean:
                bpy.data.textures.remove(tex, do_unlink=True)

        return {"FINISHED"}


def clean_duplicated_images(self, context):
    space = context.space_data
    if space.display_mode == 'ORPHAN_DATA':
        layout = self.layout
        layout.operator("image.clean_duplicated")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.OUTLINER_HT_header.append(clean_duplicated_images)


def unregister():
    bpy.types.OUTLINER_HT_header.remove(clean_duplicated_images)
    bpy.utils.unregister_module(__name__)
