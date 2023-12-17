class ComputeNode:
    def __init__(self, computeTypeStr, CPU_cycles, delay_from_BS):
        self.name = computeTypeStr
        self.CPU_cycles = CPU_cycles
        self.delay_from_BS = delay_from_BS
        print(self.name + "-compute-node with CPU_cycles:" + str(self.CPU_cycles) + ", delay-from-BS:" + str(self.delay_from_BS))