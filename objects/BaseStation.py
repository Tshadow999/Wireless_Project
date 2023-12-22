import random
import numpy as np
import util


class BaseStation:
    def __init__(self, id, bandwidth, power, x, y, frequency):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.power = power
        self.bandwidth = bandwidth
        self.frequency = frequency
        print("BS is generated")

    def allocateResources(self, edgeComputeResources, cloudComputeResources, IoTnodes, scheme="EDGE"):
        # This is the function you need to implement your decision approach
        # To give you some idea, three very simple decision logic are implemented: only-edge, only-cloud, and random
        n_nodes = len(IoTnodes)
        decision = []
        remainingEdgeCapacity = edgeComputeResources.CPU_cycles
        remainingCloudCapacity = cloudComputeResources.CPU_cycles

        if scheme == "EDGE":
            for IoT in IoTnodes:
                uplink_bandwidth = self.bandwidth / n_nodes  # equally allocate the uplink bandwidth among IoT devices
                run_on_edge = 1  # since this is EDGE allocation, set this to true
                run_on_cloud = 0
                compute_allocated = min(IoT.CPU_needed, edgeComputeResources.CPU_cycles / n_nodes)

                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        elif scheme == "CLOUD":
            for IoT in IoTnodes:
                uplink_bandwidth = self.bandwidth / n_nodes
                run_on_edge = 0
                run_on_cloud = 1
                compute_allocated = min(IoT.CPU_needed, cloudComputeResources.CPU_cycles / n_nodes)
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        elif scheme == "DIST":
            max_distance = 180
            threshold_distance = 121.0
            for IoT in IoTnodes:
                distance_to_bs = util.distance_2d(self.x, self.y, IoT.x, IoT.y)
                run_on_edge = 0
                run_on_cloud = 0
                # Use a threshold distance to decide whether to allocate to edge or cloud
                if distance_to_bs <= threshold_distance:
                    compute_allocated = min(IoT.CPU_needed, edgeComputeResources.CPU_cycles)
                    run_on_edge = 1
                else:
                    compute_allocated = min(IoT.CPU_needed, cloudComputeResources.CPU_cycles)
                    run_on_cloud = 1

                # Update remaining capacities
                remainingEdgeCapacity -= compute_allocated * run_on_edge
                remainingCloudCapacity -= compute_allocated * run_on_cloud

                # Allocate uplink bandwidth dependent on distance
                uplink_bandwidth = self.bandwidth * (max_distance - distance_to_bs) / (max_distance * n_nodes)

                # Create an Allocation object and add it to the decision list
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        # This scheme sorts the node by delay budget and cpu needed 
        # to make sure all nodes with tight delay budget constrains
        # are being assigned to the edge server. The sort on CPU requrement
        # is be able to assign as many nodes a possible to the edge server
        elif scheme == 'SORT':
            sortedIoT = sorted(IoTnodes, key=lambda x: x.CPU_needed)  # Sort on CPU requirment per IoT node
            sortedIoT.sort(key=lambda x: x.delay_budget)  # Sort on delay budget per IoT node
            decisionPID = np.empty([0, 2])
            million = 1_000_000
            for IoT in sortedIoT:
                run_on_edge = 0
                run_on_cloud = 0

                #Lower the bandwidth until the data rate is too low
                uplink_bandwidth = self.bandwidth
                rate = 0
                while IoT.get_rate(self, uplink_bandwidth) > IoT.data_generated * million:
                    # print(max(1, 0.001 * (IoT.get_rate(self, uplink_bandwidth) - IoT.data_generated * million)))
                    rate = max(1, 0.001 * (IoT.get_rate(self, uplink_bandwidth) - IoT.data_generated * million))
                    uplink_bandwidth -= rate
                uplink_bandwidth += rate

                #Distribute computing to all nodes with first come first serve for the edge server as nodes are sorted
                compute_allocated = IoT.CPU_needed
                if remainingEdgeCapacity >= IoT.CPU_needed:
                    run_on_edge = 1
                    remainingEdgeCapacity -= compute_allocated
                elif remainingCloudCapacity >= IoT.CPU_needed:
                    run_on_cloud = 1
                    remainingCloudCapacity -= compute_allocated
                else:
                    print("Not enough total computation capacity")
                
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                # Sort on ID to get back to correct order
                decisionPID = np.append(decisionPID,[[int(IoT.id), resources_allocated]], axis=0)

                # print(str(IoT.id) + " Delay: " + str(IoT.delay_budget) + " CPU: " + str(IoT.CPU_needed) + " Required BW: " + str(IoT.data_generated) + " BW allocated: " + str(int(IoT.get_rate(self,uplink_bandwidth))/1000000) + " Bandwidth: " + str(uplink_bandwidth))
            decision = decisionPID[decisionPID[:, 0].argsort()][:, 1]
        else:
            # RANDOM
            for IoT in IoTnodes:
                uplink_bandwidth = self.bandwidth / n_nodes
                trow_a_dice = random.random()
                if trow_a_dice >= 0.5:
                    run_on_edge = 0
                    run_on_cloud = 1
                    compute_allocated = min(IoT.CPU_needed, int(remainingCloudCapacity * trow_a_dice))
                    remainingCloudCapacity -= compute_allocated
                else:
                    run_on_edge = 1
                    run_on_cloud = 0
                    compute_allocated = min(IoT.CPU_needed, int(remainingEdgeCapacity * trow_a_dice))
                    remainingEdgeCapacity -= compute_allocated
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        return decision

    def check_if_feasible(self, allocation, edgeComputeCapacity, cloudComputeCapacity):
        sum_bw = 0.0
        sum_edge_compute = 0.0
        sum_cloud_compute = 0.0

        for a in allocation:
            sum_bw = sum_bw + a.uplink_bandwidth
            sum_edge_compute = sum_edge_compute + a.run_on_edge * a.compute_allocated
            sum_cloud_compute = sum_cloud_compute + (1 - a.run_on_edge) * a.compute_allocated

        utilization_uplink = sum_bw / self.bandwidth
        utilization_edge = sum_edge_compute / edgeComputeCapacity
        utilization_cloud = sum_cloud_compute / cloudComputeCapacity

        if utilization_uplink <= 1.0 and utilization_edge <= 1.0 and utilization_cloud <= 1.0:
            return True, utilization_uplink, utilization_edge, utilization_cloud
        return False, utilization_uplink, utilization_edge, utilization_cloud

    def check_node_utilization(self, allocation, edgeComputeNode, cloudComputeNode, IoT_devices):
        averageNodeDelay = 0
        nodeComputeUtil = 0
        nodeCloudUtil = 0
        for n, node in enumerate(allocation):
            averageNodeDelay += node.run_on_cloud * cloudComputeNode.delay_from_BS + node.run_on_edge * edgeComputeNode.delay_from_BS
            nodeComputeUtil += min(1, node.compute_allocated/IoT_devices[n].CPU_needed)
            nodeCloudUtil += min(1, IoT_devices[n].get_rate(self, node.uplink_bandwidth)/IoT_devices[n].data_generated)

        averageNodeDelay = averageNodeDelay / len(allocation)
        nodeComputeUtil = nodeComputeUtil / len(allocation)
        nodeCloudUtil = nodeCloudUtil / len(allocation)
        return averageNodeDelay, nodeComputeUtil, nodeCloudUtil

class Allocation:
    def __init__(self):
        self.run_on_edge = 0
        self.run_on_cloud = 0
        self.uplink_bandwidth = 0
        self.compute_allocated = 0

    def set_values(self, run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated):
        self.run_on_edge = run_on_edge
        self.run_on_cloud = run_on_cloud
        self.uplink_bandwidth = uplink_bandwidth
        self.compute_allocated = compute_allocated
