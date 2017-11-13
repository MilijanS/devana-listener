import telnetlib
import pickle
import os
import time
import concurrent.futures

host = r'host.domain' #telnet service address to check all ports
    
start_port = 0
end_port = 65535
tn = telnetlib.Telnet()


class Report:
    
    def __init__(self, data, port_num):
        self.data = data
        self.port_number = port_num
        
    def print_formatted(self):
        text = 'Data read listening to port number {0}:\n'.format(self.port_number)
        text += str(self.data)
        text += '\n'
        print(text)
            

def reset_log():
    try:
        os.remove('log.pickle')
    except Exception as e:
        print(e)

class Log:
    
    def __init__(self):
        self.last_checked_port = 0
        self.time_elapsed = 0
        self.reports = []

    def avg_time_per_port(self):
        if self.last_checked_port != 0:
            return self.time_elapsed / self.last_checked_port
        else:
            return 0
        
    def append_report(self, report):
        self.reports.append(report)
        
    def increase_time_elapsed(self, t):
        self.time_elapsed += t
        
    def print_log(self):
        for report in self.reports:
            report.print_formatted()
    
#some initialization
log = Log()
ports = [x for x in range(start_port, end_port)]
        
try:
    starting_time = time.time()
    global start_port
    pickled_log = open("log.pickle", "rb")
    log = pickle.load(pickled_log)
    pickled_log.close()
    start_port = log.last_checked_port
    PICKLE_LOADED = True
except Exception as e:
    print(e)
    start_port = 0

print('Continuing testing ports from port\n', start_port)



def check_port(tn, host, port, log):
    try:
            print('Trying port number {0}'.format(port))
            tn.open(host, port)            
    except Exception:
            print('No data at port {0}'.format(port))
    else:
            print('Found data at port number {0}'.format(port))
            data=tn.read_all()
            report = Report(data, port)
            log.reports.append(report)
    finally:
            log.last_checked_port = port
            tn.close()        
    
            
def check_all_ports_in_parallel():
    
    try:
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:            
            future_to_port = {executor.submit(check_port, tn, host, port, log): port for port in ports}         
            
    finally:
        
        print("\nCleaning up\n")
        tn.close()
     
        session_duration = time.time() - starting_time
        print("Current session lasted for {0} seconds\n".format(session_duration))
    
        log.increase_time_elapsed(session_duration)
    
        print("Total time spent testing ports :{0} seconds\n".format(log.time_elapsed))
    
        print("Average time per one port check: {0} seconds".format(log.avg_time_per_port()))
        pickle.dump(log, open("log.pickle", "wb"))
  
        
###main###
check_all_ports_in_parallel()
log.print_log()

    
    
    
