# Research

=====================================================================================
look into ubulk manifest

=====================================================================================
Links:
https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Projects/FModuleDescriptor
https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Projects/FProjectDescriptor
https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Projects/FPluginDescriptor
https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-build-tool-target-reference
https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-automation-tool-for-unreal-engine
https://dev.epicgames.com/documentation/en-us/unreal-engine/buildgraph-script-tasks-reference-for-unreal-engine#pakfile
https://dev.epicgames.com/documentation/en-us/unreal-engine/create-an-automation-project-in-unreal-engine#addcodetoanautomationscript

=====================================================================================
Commands:
ResavePluginDescriptors
ResaveProjectDescriptors

=====================================================================================
Parameters:
?-WriteBackMetadataToAssetRegistry=Disabled? maybe why iostore broken with scanning in new asset reg

=====================================================================================
CreateIoStoreContainerFiles:
sign
NoDirectoryIndex
PatchCryptoKeys=
GameOrder=
CookerOrder=
-csvoutput
-compressionformats=
-compressionformat=
-alignformemorymapping=
-blocksize=
-patchpaddingalign
-MetaOutputDirectory=
-MetaInputDirectory=
Commands=
	Output=
	ContainerName=
	PatchSource=
	GenerateDiffPatch
	PatchTarget=
	ResponseFile=
	EncryptionKeyOverrideGuid=

BasedOnReleaseVersionPath=
DLCFile=
	RemapPluginContentToGame

CreateGlobalContainer=
TargetPlatform=
CookedDirectory=
CreateContentPatch
List=
csv=
Describe=
PackageFilter=
DumpToFile=
IncludeExportHashes

=====================================================================================
Files:
D:\unreal_engine_installs\UE_4.26\Engine\Source\Developer\IoStoreUtilities\Private\IoStoreUtilities.cpp

=====================================================================================
Automation Help:

Executes scripted commands

AutomationTool.exe [-verbose] [-compileonly] [-p4] Command0 [-Arg0 -Arg1 -Arg2 ...] Command1 [-Arg0 -Arg1 ...] Command2 [-Arg0 ...] Commandn ... [EnvVar0=MyValue0 ... EnvWarn=MyValuen]

Parameters:

    -verbose                Enables verbose logging
    -nop4                   Disables Perforce functionality (default if not run on a build machine)
    -p4                     Enables Perforce functionality (default if run on a build machine)
    -compileonly            Does not run any commands, only compiles them
    -compile                Dynamically compiles all commands (otherwise assumes they are already built)
    -help                   Displays help
    -list                   Lists all available commands
    -submit                 Allows UAT command to submit changes
    -nosubmit               Prevents any submit attempts
    -nokill                 Does not kill any spawned processes on exit
    -ignorejunk             Prevents UBT from cleaning junk files
    -UseLocalBuildStorage   Allows you to use local storage for your root build storage dir (default of P:\Builds (on PC) is changed to Engine\Saved\LocalBuilds). Used for local testing.
AutomationTool exiting with ExitCode=0 (Success)

=====================================================================================
Plugin Information:

"You can also organize Plugins into subdirectories under the base Plugins folder. The engine will scan all of your sub-folders under the base Plugins folder for Plugins to load, but it will never scan subdirectories beneath a Plugin that has already been found."

"Plugins that do not have a Source folder are ignored by the project generator and will not appear in your C++ project files, but they will still be loaded at start-up as long as binary files exist."

For Plugins that contain code, the "Modules" field in the descriptor file will contain at least one entry. An example entry follows:

{
    "Name" : "UObjectPlugin",
    "Type" : "Developer"
    "LoadingPhase" : "Default"
}

Each entry requires the "Name" and "Type" fields. "Name" is the unique name of the Plugin Module that will be loaded with the Plugin. At runtime, the Engine will expect appropriate Plugin binaries to exist in the Plugin's "Binaries" folder with the specified Module name. For Modules that have a Source directory, a matching ".Build.cs" file much exist within the Module's subfolder tree. "Type" sets the type of Module. Valid options are Runtime, RuntimeNoCommandlet, Developer, Editor, EditorNoCommandlet, and Program. This type determines which types of applications can load the Module. For example, some plugins may include modules that should only load when the Editor is running. Runtime modules will be loaded in all cases, even in shipped games. Developer modules will only be loaded in development runtime or Editor builds, but never in shipping builds. Editor modules will only be loaded when the editor is starting up. Your Plugin can use a combination of modules of different types.

Along with the descriptor file, Plugins need an icon to display in the Editor's Plugin Browser. The image should be a 128x128 .png file called "Icon128.png" and kept in the Plugin's "/Resources/" directory.

=====================================================================================
BuildPlugin Help:

Builds a plugin, and packages it for distribution

Parameters:

    -Plugin                 Specify the path to the descriptor file for the plugin that should be packaged
    -NoHostPlatform         Prevent compiling for the editor platform on the host
    -TargetPlatforms        Specify a list of target platforms to build, separated by '+' characters (eg. -TargetPlatforms=Win32+Win64). Default is all the Rocket target platforms.
    -Package                The path which the build artifacts should be packaged to, ready for distribution.
    -StrictIncludes         Disables precompiled headers and unity build in order to check all source files have self-contained headers.
    -Unversioned            Do not embed the current engine version into the descriptor
AutomationTool exiting with ExitCode=0 (Success)

=====================================================================================



Projects to look into:
https://github.com/PyO3/maturin
https://github.com/PyO3/pyo3
https://github.com/ofek/venum
https://github.com/ofek/userpath
https://github.com/ofek/privy
https://github.com/scientific-python/lazy-loader
