  #Real time graphing Version 4.2
#last updated June 2nd 2021
#Authors: Hank Bethel
#Co-Authors:
#aknowledgements: Professor K J Hass
#Overview
# this code is a draft of code being used to graph data from the Mach
# Effect sensor. For contextual purposes realting to this code: the 
# Mach effect sensor is a sensor which comprises of 8 arms, A-H. On each
# arm are 6 batteries being used as sensors. In total, 48 sensors, plus
# a reading from a shunt resistor, so 56 total readings. The 
# research team is interested in the reading the voltage of the
# of each battery and graphing it in real time, that is the purpose of
# this code. The current hardware setup is 8 MCC118 DAQ hats and a
# raspberry pi 4. Each of the 8 MC118 boards is dedicated to one of the
# arms of the system, 0:A, 1:B, 2:C, ... 7:H.
#
# How this code works:
#	This code takes 7 voltage readings and adds them to a dictionary.
#	The dictionary keys correspond to the sensor number
#	as explained in the code. Then the corresponding list for each 
#	MC118 board/Arm of the system is appended in a way that each
#	read value is added to its corresponding sublist. This all occurs
#	sequentially from Board(0)/Arm_A - Board(7)/Arm_H. Then, a graph
# 	is made. Each arm has its own subplot, and each subplot graphs
#	all 7 of its voltage readings. The graph is continuosly updated
# 	to provide a live graph. Multi-threading is used to run the logging
#	program as well, using the internal clock, The csv File titled
#	exp_data.csv is written to. The data file can be taken off the
# 	device.
#
#	important notes: When conducting an experiment, create the name of the 
#	file in the code, in the log function
#	this will create a new csv file for that exact experiment. 
#	Format must be a string, and end in .csv, ie : 'example.csv'.
#	The values written to the csv file are appended, meaning that the
#	file will not be overwritten. However, if the program is stopped
#	and restarted mid expirement, the time that is written will be
#	altered. This can be fixed post experiment, 
#	but introduces error with timing in the graphs because of the 
#	missed values while the program is not running. ie: 
#	DO NOT STOP THE PROGRAM UNTIL THE EXPERIMENT IS DONE
#
#	When exported, the csv file will
#	be in the format: Board #, **newline**, Time in seconds, channel 0,
# 	channel 1, channel 2, ... channel 7. The values are the raw 
#	voltage values from the channels.  The time is the delta t 
#	from the start of recording the values. 
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.axes as axes
from daqhats import hat_list, HatIDs, mcc118
import daqhats

from itertools import count

'''x is used as the x values for graphing, the end goal would for this
list to be able to represent time when graphing. However, for now, it
is just used as tick marks for graphs. t_call is used as an itteration
count in the main code'''
index = count()
t_call = 0
x =[]

########################################################################
########################################################################
'''the list dictionary is used for graphing purposes. For each Arm of
the system, A-H, there are 7 read values. the list dictionary
creates an easy way of itterating through each main list, and then each
sublist. the list_dictionary can be called, and then its sublist can be
called as well when needed.'''

#creating an empty list for each Arm of the system:
list_A = []
list_B = []
list_C = []
list_D = []
list_E = []	
list_F = []
list_G = []
list_H = []
'''creating a dictionary for itteration purposes'''
list_dictionary = {0: list_A, 1: list_B, 2: list_C, 3: list_D, 
4: list_E, 5: list_F, 6: list_G, 7:list_H}

for j in range(8):
	for i in range (7):
#		adds 7 empty sublists to each list
		list_dictionary[j].append([])
########################################################################
########################################################################
'''aquiring the list of detected boards'''
board_list = hat_list(filter_by_id = HatIDs.ANY)
########################################################################
########################################################################
'''used for graphing/color coding each battery/sensor'''
color_dict = { 0:"k", 1:'b', 2:'g', 3:'r', 4:'c', 5: 'm', 6:'y'}
########################################################################
########################################################################
'''make sure all boards are detected'''
if not board_list:
    print("No boards found")
    sys.exit()

global BOARD_LIST  
BOARD_LIST = ['0','1','2','3','4','5','6','7']
for board_num in range(8):
	BOARD_LIST[board_num] = mcc118(board_num)

########################################################################
########################################################################
'''the data dictionary was my way of creating a temporary way of storing
the aquired voltage values. This was an easy way to itterate through
the 56 values of the system.'''
data_dic={0:0, 1:0, 2:0 , 3:0, 4:0, 5:0, 6:0,}
#for itteration purposes and ease of coding, 0 (V1)	 refers to the 1st
#battery, 1 the 2nd, 2 the 3rd, 3 the 4th, 4 the 5th,
#5 the 6th, and 6 (V7) being the Shunt resistor voltage reading.

#the function add_dic is used to act somewhat like a stack, temporaily 
#storing the current voltage reading from the current MC118 board
# and storing it with an interger key. As shown in the main loop  the
#corresponding board would then be appended with the corresponding list,
#and the value from the MC118 would be stored in the corresponding
# sublist
def add_dic (v1,v2,v3,v4,v5,v6,v7):
	data_dic[0] = v1
	data_dic[1] = v2
	data_dic[2] = v3
	data_dic[3] = v4
	data_dic[4] = v5
	data_dic[5] = v6
	data_dic[6] = v7
	return data_dic
########################################################################
########################################################################

# Change pin assignments 5/2/22
def get_voltage(board):
	channel_0 = board.a_in_read(2)
	channel_1 = board.a_in_read(3)
	channel_2 = board.a_in_read(2)
	channel_3 = board.a_in_read(3)
	channel_4 = board.a_in_read(4)
	channel_5 = board.a_in_read(5)
	channel_6 = board.a_in_read(6)
	channel_7 = board.a_in_read(7)
	# Change  channel names below
	V1=round(channel_0-channel_1,4)
	V2=round(channel_2-channel_2,4)
	V3=round(channel_0-channel_1,4)
	V4=round(channel_2-channel_2,4)
	V5=round(channel_2-channel_2,4)
	V6=round(channel_2-channel_2,4)
	V7=round(channel_2-channel_2,4)
	add_dic(V1,V2,V3,V4,V5,V6,V7)
	
########################################################################
########################################################################
########################################################################
'''this is for the function for graphing'''
left = 0
right = 300
bottom = -2
top = 2
xticks = [0,right]

plt.ion()
fig = plt.figure(figsize = (18,9))

Arm_A = plt.subplot((421),title = 'A')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_A,xticks)

Arm_B = plt.subplot(422,title='B')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_B,xticks)

Arm_C = plt.subplot(423, title='C')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_C,xticks)

Arm_D = plt.subplot(424,title='D')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_D,xticks)

Arm_E = plt.subplot(425,title = 'E')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_E,xticks)

Arm_F = plt.subplot(426,title='F')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_F,xticks)

Arm_G = plt.subplot(427,title='G')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_G,xticks)

Arm_H = plt.subplot(428,title='H')
plt.xlim(left,right)
plt.ylim(bottom,top)
axes.Axes.set_xticks(Arm_H,xticks)

plt.subplots_adjust(hspace=.4)

Arm_dic = {0:Arm_A, 1:Arm_B,2:Arm_C, 3:Arm_D, 4:Arm_E, 5:Arm_F, 6:Arm_G,
7:Arm_H}


graph_A_list = []
graph_B_list = []
graph_C_list = []
graph_D_list = []
graph_E_list = []
graph_F_list = []
graph_G_list = []
graph_H_list = []

Graph_List_Dic = { 0:graph_A_list, 1: graph_B_list, 2: graph_C_list,
3 : graph_D_list, 4: graph_E_list, 5: graph_F_list, 6: graph_G_list,
7: graph_H_list}

for j in range(8):
	for k in range(7):

		Graph_List_Dic[j].append(str(k))
	for q in range(7):
		Graph_List_Dic[j][q], = Arm_dic[j].plot(x, list_dictionary[j][i][:], color_dict[q])

fig.legend((graph_A_list[0],graph_A_list[1],graph_A_list[2], \
graph_A_list[3],graph_A_list[4],graph_A_list[5], \
graph_A_list[6]),('B1','B2','B3','B4','B5','B6','SR'),\
loc = 'upper right')


plt.show(block=False)

def animate_2():
	for i in range(7):

		graph_A_list[i].set_xdata(x)
		graph_A_list[i].set_ydata(list_A[i])

		graph_B_list[i].set_xdata(x)
		graph_B_list[i].set_ydata(list_B[i])

		graph_C_list[i].set_xdata(x)
		graph_C_list[i].set_ydata(list_C[i])

		graph_D_list[i].set_xdata(x)
		graph_D_list[i].set_ydata(list_D[i])

		graph_E_list[i].set_xdata(x)
		graph_E_list[i].set_ydata(list_E[i])

		graph_F_list[i].set_xdata(x)
		graph_F_list[i].set_ydata(list_F[i])

		graph_G_list[i].set_xdata(x)
		graph_G_list[i].set_ydata(list_G[i])

		graph_H_list[i].set_xdata(x)
		graph_H_list[i].set_ydata(list_H[i])
	fig.canvas.draw()
########################################################################
###### ENTER EXPIRIMENT CSV FILE NAME BELOW IN file_name ###############
########################################################################
########################################################################
########################################################################
########################################################################
def logging_data():								########################
	from datetime import datetime				########################
	file_path = '/home/macheffect2022/Experiment_Data_files/'#######################
	file_name = 'beta_3.csv'			################
	file_path = file_path + file_name			########################
	t0 = time.time()							########################
	log = open(file_path, 'a')					########################
########################################################################
######## ENTER EXPIRIMENT CSV FILE NAME ABOVE IN file_name #############			
###############DO NOT CHANGE ANYTHING ELSE #############################
########################################################################
########################################################################
	
	# Change pin assignments 5/2/22
	while True:	
		delta_t = (time.time()-t0)
		for board_num in range(8):
			channel_0 = BOARD_LIST[board_num].a_in_read(0)
			channel_1 = BOARD_LIST[board_num].a_in_read(1)
			channel_2 = BOARD_LIST[board_num].a_in_read(2)
			channel_3 = BOARD_LIST[board_num].a_in_read(3)
			channel_4 = BOARD_LIST[board_num].a_in_read(4)
			channel_5 = BOARD_LIST[board_num].a_in_read(5)
			channel_6 = BOARD_LIST[board_num].a_in_read(6)
			channel_7 = BOARD_LIST[board_num].a_in_read(7)
			# change channel names below
			V1=str(round(channel_6-channel_4,4))
			V2=str(round(channel_4-channel_2,4))
			V3=str(round(channel_2-channel_0,4))
			V4=str(round(channel_0-channel_1,4))
			V5=str(round(channel_1-channel_7,4))
			V6=str(round(channel_7-channel_3,4))
			V7=str(round(channel_3-channel_5,4))
			
			log.write("{0}, {1},\
			{2},{3},{4},{5},{6},{7},{8}\n"\
			.format(board_num,delta_t, V1, V2,\
			V3, V4, V5, V6, V7))
		time.sleep(.5)



'''main loop'''
def main_loop():
	while True:			
		for board_num in range(8):
			get_voltage(BOARD_LIST[board_num])
			for i in range(7):
				list_dictionary[board_num][i].append(data_dic[i])
		t_call = next(index)
		x.append(t_call)
		time.sleep(1)
		animate_2()	
while True:
	import threading
	t2 = threading.Thread(target = logging_data, name = 'thread2')
	t2.start()
	main_loop()


