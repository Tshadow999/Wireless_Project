import util
from objects import Params, BaseStation, IoT, ComputeNode
import numpy as np
import matplotlib.pyplot as plt

# Read the parameters from Params.py  file for the Base Station
bandwidth = Params.BS_bandwidth
power = Params.BS_power
[x, y] = Params.BS_location
frequency = Params.frequency

# Generate the BS
BS = BaseStation.BaseStation(1, bandwidth, power, x, y, frequency)

# Generate IoT devices, read from input_files folder the IoT device properties
n_IoT_devices = Params.n_IoT_devices
IoT_devices = IoT.read_from_IoT_file(Params.input_folder + "/IoT_" + str(n_IoT_devices) + "_devices.txt")

# Generate Edge and Cloud compute nodes according to the parameters in the Params.py file
edgeComputeNode = ComputeNode.ComputeNode("Edge", Params.Edge_CPU_cycles, Params.Edge_BS_delay)
cloudComputeNode = ComputeNode.ComputeNode("Cloud", Params.Cloud_CPU_cycles, Params.Cloud_BS_delay)

# Run your BS decision algorithm considering edge, cloud, and IoT properties
schemes = ["EDGE", "CLOUD", "RANDOM", "DIST", "SORT"]

stats = np.zeros((7, len(schemes)))  # 4 for 4 statistics
# Initialize an array to store QoS metrics for each scheme
qos_metrics = np.zeros((len(schemes), len(IoT_devices)))
for a, allocation_scheme in enumerate(schemes):
    allocation = BS.allocateResources(edgeComputeNode, cloudComputeNode, IoT_devices, allocation_scheme)

    # Check if the algorithm's decision is a feasible one (resource limits are not violated)
    is_feasible, utilization_uplink, utilization_edge, utilization_cloud = BS.check_if_feasible(allocation, edgeComputeNode.CPU_cycles, cloudComputeNode.CPU_cycles)

    #calculate the average delay, Computation Utilization and Cloud Utilization for each IoT node in a scheme
    averageNodeDelay, nodeComputeUtil, nodeCloudUtil = BS.check_node_utilization(allocation, edgeComputeNode, cloudComputeNode, IoT_devices)

    print("\nGreat! This is a feasible allocation of resources.\n") if is_feasible else print("There seems to be more capacity allocated than the available capacity!")


    # Report the resource utilization: uplink bandwidth, edge and cloud usage
    print("Utilization of Uplink:%.2f \nEdge-Utilization:%.2f \nCloud-Utilization:%.2f" % (utilization_uplink, utilization_edge, utilization_cloud))
    stats[:, a] = [is_feasible, utilization_uplink, utilization_edge, utilization_cloud, averageNodeDelay, nodeComputeUtil, nodeCloudUtil]

    for i, IoT_device in enumerate(IoT_devices):
        qos_metrics[a, i] = IoT_device.calculate_qos_metric(allocation[i], BS)

# Plot statistics
util.plot_bars(np.arange(len(schemes)), stats[1, :], "output_files/uplink_utilization", xlab="Allocation Schemes",
               ylab="Uplink Bandwidth Utilization", xlabels=schemes, labels=schemes)
util.plot_bars(np.arange(len(schemes)), stats[2, :], "output_files/edge_utilization", xlab="Allocation Schemes",
               ylab="Edge Compute Utilization", xlabels=schemes, labels=schemes)
util.plot_bars(np.arange(len(schemes)), stats[3, :], "output_files/cloud_utilization", xlab="Allocation Schemes",
               ylab="Cloud Compute Utilization", xlabels=schemes, labels=schemes)

util.plot_bars(np.arange(len(schemes)), stats[4, :], "output_files/node_delay", xlab="Allocation Schemes",
               ylab="Average IoT node dalay (s)", xlabels=schemes, labels=schemes)
util.plot_bars(np.arange(len(schemes)), stats[5, :], "output_files/node_compute_utilization", xlab="Allocation Schemes",
               ylab="Node Compute Utilization", xlabels=schemes, labels=schemes)
util.plot_bars(np.arange(len(schemes)), stats[6, :], "output_files/node_bandwidth_utilization", xlab="Allocation Schemes",
               ylab="NOde Bandwidth Utilization", xlabels=schemes, labels=schemes)

# Quality of service Plots
average_qos_metric = [util.average(qos_metrics[0, :]), util.average(qos_metrics[1, :]), util.average(qos_metrics[2, :]),
                      util.average(qos_metrics[3, :]), util.average(qos_metrics[4, :])]

for i, IoT_device in enumerate(IoT_devices):
    util.plot_bars(np.arange(len(schemes)), qos_metrics[:, i], f"output_files/qos_metric_iot_{IoT_device.id}",
                   xlab="Allocation Schemes", ylab=f"QoS Metric [{IoT_device.id}]", xlabels=schemes, labels=schemes)

# Plot the average qos
util.plot_bars(np.arange(len(schemes)), average_qos_metric, f"output_files/qos_metric_iot_avg",
                   xlab="Allocation Schemes", ylab=f"Average QoS Metric", xlabels=schemes, labels=schemes)

