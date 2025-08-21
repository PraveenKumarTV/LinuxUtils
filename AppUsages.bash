ps -u $USER -o comm,etimes --sort=-etimes \     
| grep -iE 'chrome|firefox|chromium|code|sublime_text|vim|nano|gnome-terminal|konsole|xterm|tilix|alacritty|slack|discord|zoom|teams|vlc|spotify' \
| awk '!seen[tolower($1)]++ {print $1, $2}' \
| while read app secs; do
    printf "%-15s %02d:%02d:%02d\n" "$app" "$((secs/3600))" "$(((secs%3600)/60))" "$((secs%60))"
done

