class AndroidSync:
    goodToGo = False
    SDCARD = "/storage/self/primary"
    
    def setup(this):
        this.goodToGo = False
        try:
            global sys, pip, sp
            sys = __import__("sys")
            pip = __import__("pip")
            sp = __import__("subprocess")
            this.goodToGo = True
            return True
        
        except ImportError as ie:
            missing = ''.join(i for i in ie).split(" ")[-1]
            print "Missing module: ", missing
            print "Downloading '%s' using pip..." % missing

            if this.install(missing):
                this.setup()
            else:
                return False

    def install(this, package):        
        if(package=="pip"):
            print "PIP required to proceed. Exiting ..."
            return False
        try:
            pip.main(["install", package])
            return True

        except:
            print "Unable to install %s using pip. Please read the instructions for manual installation.. Exiting" % package
            print "Error: %s: %s" % (exc_info()[0] ,exc_info()[1])
            return False

    def cmd(this, command):
        p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = p.communicate()
        return stdout

    def isdir(this, filepath):
        p = sp.Popen(adb+"shell cd "+filepath, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        stderr = p.communicate()[1]
        return stderr==""
        
    def run(this):
        # env setup
        if not this.setup() or not this.goodToGo:
            print "\nDependecy issues! Exiting ..."
            sys.exit(1)

        global adbpath, adb
        adbpath = 'D:/platform-tools/'
        adb = adbpath + 'adb '

        # run commands
        command = adb + 'devices'

        # script execution
        try:
            p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            stdout, stderr = p.communicate()
            device = stdout.split("\r\n")[1]

            if device=="":
                print "No device connected."
                sys.exit(0)
            elif stderr=="":
                deviceid, devicestatus = device.split("\t")
                print "Found Device: %s \nDevice Status: %s" % (deviceid, "OK" if devicestatus=="device" else devicestatus)

                this.selectDir(this.SDCARD)
        except NameError as ne:
            print ne

    def listDir(this, path, enableSelect=False):
        stdout = this.cmd(adb+" shell ls "+path)

        global directories
        directories = stdout.split("\r\n")
        
        print "\nListing %d files in %s: \n" % (len(directories)-1, path)
        
        if enableSelect:
            print "{ b: Back, s: Select }\n"

        for i in xrange(len(directories)-1):
            print "{:2d}. {:15s}".format(i,directories[i]),
            if i&1: print "\n",

            try:
                if i>0 and i%30==0:
                    raw_input("\n\nPress enter to list more or Ctrl+C to cancel...\n")
            except KeyboardInterrupt:
                break

    def selectDir(this, path):
        global adb, directories
        choice = -1
        printData = True
        try:
            while choice!="s":
                if printData:
                    this.listDir(path, True)                
                try:
                    printData = True
                    choice = raw_input("\n\nChoice> ")
                    if choice=="b":
                        if path!=this.SDCARD:
                            path = "/".join(path.split("/")[:-1])
                    elif choice=="s": break
                    elif int(choice)<0:
                        raise IndexError
                    else:
                        DIR = directories[int(choice)]
                        DIR = DIR.replace(" ", "\ ")
                        if not this.isdir(path+"/"+DIR):
                            raise Exception("Not a Directory !")
                        else:
                            path += "/"+DIR
                except ValueError, IndexError:
                    printData = False
                    print "\nInvalid Selection !",
                except Exception as e:
                    printData = False
                    print "\n",e,
                    
        except KeyboardInterrupt:
            print "Exiting!"
            sys.exit(0)

        print "Your sync path set to: %s" % path
                
if __name__ == "__main__":
    ps = AndroidSync()
    ps.run()
