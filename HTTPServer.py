import sdk.FliSdk_V2 as FliSdk
from time import sleep

context = FliSdk.Init()
# call before DetectCameras or it fails for some reason ...
grabbers_list = FliSdk.DetectGrabbers(context)
cameras_list = FliSdk.DetectCameras(context)

while len(cameras_list)==0:
    sleep(1)
    cameras_list = FliSdk.DetectCameras(context)

print(f"camera selected: {cameras_list[0]}")

# if camera is available
if cameras_list[0]!='Usb#' and len(cameras_list)>=1:
    res = FliSdk.SetCamera(context, cameras_list[0])
    FliSdk.Update(context)
else:
    raise ConnectionError("No camera found...")

if FliSdk.IsCredTwo(context):
    res = False
    while not res:
        res = FliSdk.FliCredTwo.StartHttpServer(context)
    res, ip = False, ""
    while not res or ip=="":
        res, ip = FliSdk.FliCredTwo.GetIpAddress(context)
    print(ip)
    res, password = False, ""
    while not res or password=="":
        res, password = FliSdk.FliCred.GetSshPassword(context)
    print(password)
else:
    raise NotImplementedError("")

with open('httpserver.txt', 'a') as f:
    f.write(f"{cameras_list[0]}")
    f.write(f"IP-ADDRESS {ip}")
    f.write(f"PASSWORD {password}")


