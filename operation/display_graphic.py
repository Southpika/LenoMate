import pynvml


class operation():
    def fit(self):
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        print(f"Total memory: {info.total/1024**2:.2f} MB")
        print(f"Free memory: {info.free/1024**2:.2f} MB")
        print(f"Used memory: {info.used/1024**2:.2f} MB")
        
if __name__ == '__main__':
    opt = operation()
    opt.fit()