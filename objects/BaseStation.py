import random

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
                compute_allocated = edgeComputeResources.CPU_cycles / n_nodes  # JUST allocate resources equally among IoT devices
                if compute_allocated > IoT.CPU_needed:  # if allocated resource is larger than needed, set allocation to what is needed
                    compute_allocated = IoT.CPU_needed
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        elif scheme == "CLOUD":
            for IoT in IoTnodes:
                uplink_bandwidth = self.bandwidth / n_nodes
                run_on_edge = 0
                run_on_cloud = 1
                compute_allocated = cloudComputeResources.CPU_cycles / n_nodes
                if compute_allocated > IoT.CPU_needed:  # if allocated resource is larger than needed, set allocation to what is needed
                    compute_allocated = IoT.CPU_needed
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        elif scheme == "MINE":
            max_distance = 200
            for IoT in IoTnodes:
                # Do stuff here
                distance_to_bs = util.distance_2d(self.x, self.y, IoT.x, IoT.y)

                # Use a threshold distance to decide whether to allocate to edge or cloud
                threshold_distance = 75.0  # Adjust this threshold as needed
                if distance_to_bs <= threshold_distance:
                    compute_allocated = min(IoT.CPU_needed, edgeComputeResources.CPU_cycles)
                    run_on_edge = 1
                    run_on_cloud = 0
                else:
                    compute_allocated = min(IoT.CPU_needed, cloudComputeResources.CPU_cycles)
                    run_on_edge = 0
                    run_on_cloud = 1

                # Update remaining capacities
                remainingEdgeCapacity -= compute_allocated * run_on_edge
                remainingCloudCapacity -= compute_allocated * run_on_cloud

                # Allocate uplink bandwidth dependent on distance
                uplink_bandwidth = self.bandwidth * (max_distance - distance_to_bs) / max_distance / n_nodes

                print(IoT.get_rate(self, uplink_bandwidth))
                # Create an Allocation object and add it to the decision list
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        else:
            for IoT in IoTnodes:
                uplink_bandwidth = self.bandwidth / n_nodes
                trow_a_dice = random.random()
                if trow_a_dice >= 0.5:
                    run_on_edge = 0
                    run_on_cloud = 1
                    compute_allocated = int(remainingCloudCapacity * trow_a_dice)
                    if compute_allocated > IoT.CPU_needed:  # if allocated resource is larger than needed, set allocation to what is needed
                        compute_allocated = IoT.CPU_needed
                    remainingCloudCapacity -= compute_allocated
                else:
                    run_on_edge = 1
                    run_on_cloud = 0
                    compute_allocated = int(remainingEdgeCapacity * trow_a_dice)
                    if compute_allocated > IoT.CPU_needed:  # if allocated resource is larger than needed, set allocation to what is needed
                        compute_allocated = IoT.CPU_needed
                    remainingEdgeCapacity -= compute_allocated
                resources_allocated = Allocation()
                resources_allocated.set_values(run_on_edge, run_on_cloud, uplink_bandwidth, compute_allocated)
                decision.append(resources_allocated)

        return decision

    def check_if_feasible(self, allocation, edgeComputeCapacity, cloudComputeCapacity):
        sum_bw = 0
        sum_edge_compute = 0
        sum_cloud_compute = 0

        for a in allocation:
            sum_bw = sum_bw + a.uplink_bandwidth
            sum_edge_compute = sum_edge_compute + a.run_on_edge * a.compute_allocated
            sum_cloud_compute = sum_cloud_compute + (1 - a.run_on_edge) * a.compute_allocated

        utilization_uplink = 1.0 * sum_bw / self.bandwidth
        utilization_edge = 1.0 * sum_edge_compute / edgeComputeCapacity
        utilization_cloud = 1.0 * sum_cloud_compute / cloudComputeCapacity

        if utilization_uplink <= 1.0:
            if utilization_edge <= 1.0:
                if utilization_cloud <= 1.0:
                    return True, utilization_uplink, utilization_edge, utilization_cloud
        return False, utilization_uplink, utilization_edge, utilization_cloud


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