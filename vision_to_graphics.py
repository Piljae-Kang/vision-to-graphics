import mitsuba as mi
mi.set_variant('scalar_rgb')
from mitsuba import ScalarTransform4f as T
import readchar
import quaternion
import math

scene = mi.load_dict({
    'type': 'scene',
    # The keys below correspond to object IDs and can be chosen arbitrarily
    'integrator': {'type': 'path'},
    'light': {'type': 'constant'},
    'myshape': {
        'type': 'ply',
        'filename': '/home/piljae/photo_data/building/dense/meshed-delaunay2.ply'
        
    }
})

#'/home/piljae/photo_data/building/dense/fused.ply'
#'/home/piljae/photo_data/building/dense/meshed-delaunay.ply'
print(scene)

f = open("/home/piljae/photo_data/building/sparse/cameras.txt", 'r')

width = 0
height = 0
f_length = 0
principal_point_x = 0
principal_point_y = 0


while True:
    line = f.readline()
    str_arr = line.split(" ")
    if not str_arr[0] == "#":
        width = int(str_arr[2])
        height = int(str_arr[3])
        f_length = float(str_arr[4])
        principal_point_x = int(str_arr[5])
        principal_point_y = int(str_arr[6])
        f.close()
        break


print("#################################################################")
print(width)
print(height)
print(f_length)


def function(Q, T_list):
	import numpy as np

	n = Q[0]
	e1 = Q[1]
	e2 = Q[2]
	e3 = Q[3]
	t0 = T_list[0]
	t1 = T_list[1]
	t2 = T_list[2]
	
	print("this is 3x3 matrix of quaternion")
	q_mat = quaternion.as_rotation_matrix(np.quaternion(n, e1, e2, e3))
	

	# 4x4 rotation matrix
	rot_matrix = np.array([[q_mat[0][0], q_mat[0][1], q_mat[0][2], 0],
		                [q_mat[1][0], q_mat[1][1], q_mat[1][2], 0],
		                [q_mat[2][0], q_mat[2][1], q_mat[2][2], 0],
		                [0, 0, 0, 1]])



	R = np.array([[q_mat[0][0], q_mat[0][1], q_mat[0][2]],
		                [q_mat[1][0], q_mat[1][1], q_mat[1][2]],
		                [q_mat[2][0], q_mat[2][1], q_mat[2][2]]])

	TT = np.array([[t0],[t1], [t2]])

	

	R = (-1) * np.linalg.inv(R)
	print("-R^t")
	print(R)
	print("T")
	print(TT)

	print("-R^t * T : ")
	print(R@TT)


	camera_center = R@TT

	x_axis = [q_mat[0][0], q_mat[0][1], q_mat[0][2]]

	y_axis = [q_mat[1][0], q_mat[1][1], q_mat[1][2]]
	
	z_axis = [q_mat[2][0], q_mat[2][1], q_mat[2][2]]

	print("###################################################################")


	for i in range(10):
		print("%0.4f %0.4f %0.4f" %(camera_center[0][0] + z_axis[0] * i/10, camera_center[1][0] + z_axis[1] * i/10, camera_center[2][0] + z_axis[2] * i/10))



	new_matrix = np.array([[q_mat[0][0], q_mat[1][0], q_mat[2][0], t0],
		                [q_mat[0][1], q_mat[1][1], q_mat[2][1], t1],
		                [q_mat[0][2], q_mat[1][2], q_mat[2][2], t2],
		                [0, 0, 0, 1]])
	
	change_matrix = np.array([[1, 0, 0, 0],     # change_matrix = mi.Transform4f.rotate([1, 0, 0], 180)
				 [0, -1, 0, 0], 
				 [0, 0, -1, 0], 
				 [0, 0, 0, 1]])
	change_matrix = mi.Transform4f(change_matrix)
 
	eye_negative = [-camera_center[0][0], -camera_center[1][0], -camera_center[2][0]] # T(-e)를 위해 카메라 좌표의 - 부호 붙인다.

	matrix = mi.Transform4f(rot_matrix) @ mi.Transform4f.translate(eye_negative)
	
	new_matrix = mi.Transform4f(new_matrix) 
	
	#print(rot_matrix)

	look_at = T.look_at(
	    origin=[camera_center[0][0], camera_center[1][0], camera_center[2][0],],  # 카메라 위치
	    target=[z_axis[0] + camera_center[0][0], z_axis[1] + camera_center[1][0], z_axis[2] + camera_center[2][0]],  # graphic 카메라의 참조위치
	    up=[-y_axis[0], -y_axis[1], -y_axis[2]]  # up 벡터는 y의 반대 방향 벡터로 설정
	)

	print("this is matrix :")
	print(matrix)
	print("this is look at function")
	print(look_at)
	
	#tt_list = [-T_list[0], -T_list[1], -T_list[2]]
	
	#rot_matrix = mi.Transform4f.inverse(rot_matrix) @ mi.Transform4f.translate(tt_list) @ mi.Transform4f.rotate([0, 0, 1], 180)
	#rot_matrix = mi.Transform4f.inverse(rot_matrix)
	
	
	sensor = mi.load_dict({
		'type': 'perspective',
		'fov': 61.9,
		'to_world': look_at,
		'sampler': {
		    'type': 'independent',
		    'sample_count': 16
		},
		'film': {
		    'type': 'hdrfilm',
		    'width': width,
		    'height': height,
		    'rfilter': {
		        'type': 'tent',
		    },
		    'pixel_format': 'rgb',
		},
	    })
	image = mi.render(scene, sensor=sensor)

	import matplotlib.pyplot as plt

	plt.axis("off")
	plt.imshow(image)
	plt.show()

f = open("/home/piljae/photo_data/building/sparse/images.txt", 'r')
Q = [0, 0, 0, 0]
T_list = [0, 0, 0,]
count = 0
while True:
    line = f.readline()
    str_arr = line.split(" ")
    if not str_arr[0] == "#":
        count = count + 1
        if count % 2 == 0:
            continue
        Q[0] = (float(str_arr[1]))
        Q[1] = (float(str_arr[2]))
        Q[2] = (float(str_arr[3]))
        Q[3] = (float(str_arr[4]))
        T_list[0] = (float(str_arr[5]))
        T_list[1] = (float(str_arr[6]))
        T_list[2] = (float(str_arr[7]))
        print(" this is photo name : " + str_arr[9])
        function(Q, T_list)
      	#print("width: %d, height: %d, f_length: %s, principal_point_x: %d, principal_point_y: %d" %(width, height, f_length, principal_point_x, principal_point_y))
