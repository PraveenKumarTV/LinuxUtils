make the file changeDP.sh as executable

1. Edit your crontab
crontab -e

2. Add this line (replace path and user info)
0 7 * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /home/praveen/Desktop/LinuxUtils/changeDP.sh

(the above cmd is specifically for gnome and changes background image at every 7 AM)

3. DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /home/praveen/Desktop/LinuxUtils/changeDP.sh

run the cmd,if it works well you are set.
