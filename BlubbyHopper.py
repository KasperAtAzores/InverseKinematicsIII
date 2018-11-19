import bpy
from math import pi

# This method is a small perl. It joins all the objects in the obs list, without changing
# the current object. And it seems super fast
def join_objects(obs):
    scene = bpy.context.scene
    ctx = bpy.context.copy()
    # one of the objects to join
    ctx['active_object'] = obs[0]
    ctx['selected_objects'] = obs
    # we need the scene bases as well for joining
    ctx['selected_editable_bases'] = [scene.object_bases[ob.name] for ob in obs]
    bpy.ops.object.join(ctx)
    

# It seems all my programs end up with a little method which makes
# cubes - this one is appropriate for this program    
def make_cube(loc, size):
    bpy.ops.mesh.primitive_cube_add(radius=1, location=loc)
    bpy.context.object.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return bpy.context.object
    
# I am not quite sure why this one-legged creature ended up being called 
# blobber - but that is its name
def build_blobber():
    # Build the boxes
    foot = make_cube( (1,0,0.2), (4,2,0.4) )
    lower_leg = make_cube( (0,0,1.5+0.4),(2,2,3))
    upper_leg = make_cube( (0,0,1.5+0.4+3), (2,2,3))
    body = make_cube( (0,0, 1.5+0.4+6), (3,3,3))
    # Join them into one mesh
    join_objects([body, upper_leg, lower_leg, foot])
    
    # subdivide the mesh
    bpy.ops.object.editmode_toggle()
    for _ in range(5):
        bpy.ops.mesh.subdivide()
    # smooth the mesh
    for _ in range(10):
        bpy.ops.mesh.vertices_smooth()
    bpy.ops.object.editmode_toggle()
    # smooth the rendering
    bpy.ops.object.shade_smooth()
    # give it a name
    blobber = bpy.context.active_object
    blobber.name = "Blopper"
    return blobber
    
def add_armature():
    # Build the first bone of the armature
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 6.4))
    # rotate and scale it
    bpy.context.object.rotation_euler[1] = pi
    bpy.context.object.scale[2] = 3
    # apply the transformation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Setup for building the other bones
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = bpy.context.object.data.edit_bones
    # Name the first bone - created above
    upper = edit_bones[0] #bpy.context.object.data.bones[0]
    upper.name = 'Upper'
    
    # Make lower leg bone
    lower = edit_bones.new('Lower')
    # a new bone will have zero length and not be kept
    # move the head/tail to keep the bone
    lower.head = (0,0, -3)
    lower.tail = (-0.1,0, -6)
    lower.parent = upper

    # Make knee - it is used to control the leg
    knee = edit_bones.new('Knee_Pole')
    knee.head = (2,0,-3)
    knee.tail = (2.5,0,-3)

    # foot Inverse Kinematics bone
    foot_ik = edit_bones.new('Foot_IK')
    foot_ik.head = (-0.1,0,-6)
    foot_ik.tail = (-1.5,0,-6)
    
    # foot bone
    foot = edit_bones.new('Foot')
    foot.head = (0,0,-6)
    foot.tail = (2,0,-6)
    foot.parent = foot_ik
    
    # exit edit-mode 
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # set up the inverse kinematics constraint
    armature = bpy.context.scene.objects.get("Armature")
    lower_bone = armature.pose.bones.get("Lower")
    ik_constr = lower_bone.constraints.new('IK')
    ik_constr.target = armature
    ik_constr.subtarget = "Foot_IK"
    ik_constr.chain_count = 2
    ik_constr.pole_target = armature
    ik_constr.pole_subtarget = "Knee_Pole"
    ik_constr.pole_angle = 3.14159
    return armature



blobber = build_blobber()
amature = add_armature()
bpy.ops.object.select_by_type(type='MESH', extend=False)
bpy.ops.object.select_by_type(type='ARMATURE', extend=True)
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

