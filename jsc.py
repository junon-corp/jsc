import os
import json
import subprocess

path = "jsc.json"

if __name__ == "__main__":
	import sys

	args = sys.argv
	if len(args) > 1:
		if args[1] in ["-o", "--output"]:
			path = ""
			for arg in args[2:]:
				if arg.startswith('-'):
					continue
				path += arg

			try:
				open(path, 'w+')
			except FileNotFoundError:
				print("Destination directory not found.")
				exit(1)
			except PermissionError:
				print("Unable to write in destination directory.")
				exit(1)

		else:
			print("Junon Source Control tool for jue")
			print("" if args[1] in ["-h", "--help"] else f"argument \"{args[1]}\" is unknown")
			print("\t-h, --help \tDisplay this help message")
			print("\t-o, --output \tProvide a output path for the json file")
			exit(1)



	
		print(args)

gitstatus = subprocess.Popen(
	["git", "status", "--porcelain=v2", "--branch"],
	stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
stdout, stderr = gitstatus.communicate()

status = stdout.decode('utf-8')

j = {
	"branch": {
		"current_commit": "",
		"head": "",
		"upstream": {
			"is_set": False,
			"upstream": "",
			"ahead": None,
			"behind": None
		}
	},

	"files": {
		"deleted": [],
		"commited": None,
		"tracked": [],
		"untracked": []
	}
}


dir_files = os.listdir()
for line in status.split('\n'):
	line = line[2:]

	if line.startswith("branch"):
		opt = line.split(' ')[0].split('.')[1]

		if opt == "oid":
			j['branch']['current_commit'] = line.split(' ')[1]

		elif opt == "head":
			j['branch']['head'] = line.split(' ')[1]

		elif opt == "upstream":
			j['branch']['upstream']['is_set'] = True
			j['branch']['upstream']['upstream'] = line.split(' ')[1]

		elif opt == "ab":
			j['branch']['upstream']['ahead'] = int(line.split(' ')[1].strip('+-'))
			j['branch']['upstream']['behind'] = int(line.split(' ')[2].strip('+-'))

	else:
		if line.split(' ')[0] in dir_files:
			filename = line
			j['files']['untracked'].append(
				{"file": filename}
			)

		else:
			if line:
				xy, sub, mH, mI, mW, hH, hI, filepath = line.split(' ')
				file = {
					"filepath": filepath,
					"staged_status": xy[0] if xy[0] != "." else None,
					"unstaged_status": xy[1] if xy[1] != "." else None,
					"is_submodule": True if sub[0] == "S" else False,
					#"submodule": {},
					"octal_modes": {
						"head": mH,
						"index": mI,
						"worktree": mW
					},
					"obj_name": {
						"head": hH,
						"index": hI
					}
				}
				if file['is_submodule']:
					file['has_commit'] = True if sub[1] == "C" else False
					file['has_tracked_change'] = True if sub[1] == "M" else False
					file['has_untracked_change'] = True if sub[1] == "U" else False

				j['files']['tracked'].append(file)


json.dump(j, open(path, 'w'), indent=2)
