# Frequently Asked Questions (FAQ)

---

### **Table of Contents**
1. [How do I get the Unreal Engine version?](#q1)
2. [How to call an exe at a specific time?](#q2)
3. [How to kill a process at a specific time?](#q3)
4. [How to set the game window title override string?](#q4)
5. [How do I install the proper version of Unreal Engine?](#q5)
6. [How to know what to add to a mod entry?](#q6)
7. [Which pak method is best for my mod entry?](#q7)
8. [Which launch type is best for the game?](#q8)
9. [What pak dir structure should my mods use?](#q9)
10. [How do I know what files will end up in my paks?](#q10)
11. [Is my game iostore or not?](#q11)
12. [Does my game use loose file modding?](#q12)
13. [What if my game uses loose file modding?](#q13)
14. [What if my game needs to be packed with a specific uproject name?](#q14)
15. [How to install repak?](#q15)
16. [What to do if the game is iostore?](#q16)
17. [What kind of useful exe stuff can I use?](#q17)
18. [What if I need to use an asset patcher or similar tool before I package the final mod archives?](#q18)
19. [How to do a window management entry?](#q19)
20. [When would I want to set the window name?](#q20)
21. [What kind of useful window things can I do?](#q21)
22. [I have files I edited and want to consistently package, where to put these?](#q22)
23. [I have files outside the mod dir, how to include them in the mod?](#q23)
24. [What is the mod name dir name override for?](#q24)
25. [When would I want to use the working dir override?](#q25)
26. [What do you mean by mod archives?](#q26)
27. [What if I want to not package a mod temporarily but leave the entry there?](#q27)
28. [What to set the pak chunk number to?](#q28)
29. [What is manually specified assets, asset paths, and tree paths for?](#q29)
30. [What is compression type for?](#q30)
31. [What if I want plugin content in my mod?](#q31)
32. [What if I want configs in my mod?](#q32)

---

### <a name="q1"></a>1. How do I get the Unreal Engine version?
In the game win64 folder, right click on the game exe, and check its properties, often it is listed there.

---

### <a name="q2"></a>2. How to call an exe at a specific time?
You can add an entry to the alt exe entry list, and specify the path, when you want it to fire, and if it's synchronous or not.

---

### <a name="q3"></a>3. How to kill a process at a specific time?
You can add an entry to the process kill list, with a name, to kill with exact title match or all containing, and a specific time.

---

### <a name="q4"></a>4. How to set the game window title override string?
This is for finding and monitoring the game for various script functions.

---

### <a name="q5"></a>5. How do I install the proper version of Unreal Engine?
You can either compile it yourself from scratch, or download it from the Epic Games Launcher.

---

### <a name="q6"></a>6. How to know what to add to a mod entry?
So for the mod entry, the mod name is the final mod archive(s) name. The pak dir structure is the folder setup within the game's paks folder. Mod name dir type is either Content/ModName/CustomContent or Content/Mods/ModName, if your mod contents aren't in either you can use the manually specified tree and asset paths section.

---

### <a name="q7"></a>7. Which pak method is best for my mod entry?
Repak if not iostore, and engine if iostore. These are the fastest, and support compression.

---

### <a name="q8"></a>8. Which launch type is best for the game?
Launcher allows keeping online functionality, exe prevents spamming notifications on various game launchers.

---

### <a name="q9"></a>9. What pak dir structure should my mods use?
Often ~mods for most asset mods, and LogicMods for blueprint mods, there can be other conventions though.

---

### <a name="q10"></a>10. How do I know what files will end up in my paks?
For non-iostore games, the mod name dir type will include files, Content/Mods/ModName or Content/CustomContent/ModName, will be in the files, but also all trees specified in the manual tree paths, and all assets with the file name in the specified asset paths. This is for all non-engine pak enums, Data Assets/Primary Asset Labels, should be used for iostore engine packing.

---

### <a name="q11"></a>11. Is my game iostore or not?
In the game's paks directory, if you see ucas and utoc files, the game uses iostore.

---

### <a name="q12"></a>12. Does my game use loose file modding?
Most games don't, but if there is no paks folder, then that is its primary method of loading assets.

---

### <a name="q13"></a>13. What if my game uses loose file modding?
This tool works fine to copy over modded contents, but things can get a bit hairy after removing and renaming files occasionally.

---

### <a name="q14"></a>14. What if my game needs to be packed with a specific uproject name?
This is what the alt uproject name in dir name setting is for.

---

### <a name="q15"></a>15. How to install repak?
Download from here.

---

### <a name="q16"></a>16. What to do if the game is iostore?
Use the engine packing, packing enum for your mod entries, from within the engine use DA/PAL, or assign chunk ID, to tell what goes into what mod archive files.

---

### <a name="q17"></a>17. What kind of useful exe stuff can I use?
You can run asset patchers, manual packers, and anything else you need at various points in the script running.

---

### <a name="q18"></a>18. What if I need to use an asset patcher or similar tool before I package the final mod archives?
You can use the exe runner methods, or the packing dir to pak consistent edited files as well.

---

### <a name="q19"></a>19. How to do a window management entry?
You can add an entry to the window management list, and specify a window name, when to fire, and what to do to the window.

---

### <a name="q20"></a>20. When would I want to set the window name?
For use with the window management utility, and other applications.

---

### <a name="q21"></a>21. What kind of useful window things can I do?
You can move UE4SS window, game window, UnrealAutoMod window, engine window, IDE window, Unreal mod loader window, and many others to save time.

---

### <a name="q22"></a>22. I have files I edited and want to consistently package, where to put these?
Inside your mod settings JSON folder there is a packing dir. You can place various files here that will be manually packed for your mod files.

---

### <a name="q23"></a>23. I have files outside the mod dir, how to include them in the mod?
Put a tree or a single path under the manually specified assets lists.

---

### <a name="q24"></a>24. What is the mod name dir name override for?
This is for if your pak name needs _P for example, but you do not want your internal content ModName folder to have _P.

---

### <a name="q25"></a>25. When would I want to use the working dir override?
Space reasons, maybe others.

---

### <a name="q26"></a>26. What do you mean by mod archives?
Pak files for non-iostore games, pak, ucas, and utoc for iostore games.

---

### <a name="q27"></a>27. What if I want to not package a mod temporarily but leave the entry there?
You can toggle the is_enabled in its mod entry. Beware, this will delete any mods with that mod name from that packing dir structure folder it is set to.

---

### <a name="q28"></a>28. What to set the pak chunk number to?
This is for the engine packing enum, it corresponds to the number you chose within your Data Asset of type Primary Asset Label.

---

### <a name="q29"></a>29. What is manually specified assets, asset paths, and tree paths for?
This is for specifying files outside of your ModName dir to end up in your mod, often used for replacing game files.

---

### <a name="q30"></a>30. What is compression type for?
This is the type of compression used to make the mod archives.

---

### <a name="q31"></a>31. What if I want plugin content in my mod?
It supports plugins in the settings JSON packing dir, and in the manually specified assets path lists.

---

### <a name="q32"></a>32. What if I want configs in my mod?
It supports configs in the settings JSON packing dir, and in the manually specified assets path lists.
