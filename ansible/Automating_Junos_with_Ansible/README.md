The text of *Day One: Automating Junos with Ansible, 2nd Edition* walks the reader through creating a number of example playbooks and their supporting files. Some of the playbooks are revised several times in a single chapter. Some of the playbooks are revised several times across several chapters.

In order to maintain a "flow" the book does not ask the reader to save the revisions to the playbooks and supporting files using different, versioned names (for example, "save playbook-2.yaml as playbook-3.yaml"). Instead, the book assumes the reader will keep revising the files "in place." (This is also, in the author's experience, closer to how scripts and playbooks evolve in the real world.)

However, this lack of versioning creates a problem when trying to represent the files at different states of their evolution, which is the goal of the book's directory in Juniper's GitHub repository. The files in this directory are "versioned" in two ways:

- Playbooks and supporting files from each chapter are in chapter-specific directories. Chapter 8 has two directories because of the changes made to the inventory file during the chapter.

- Some of the playbooks and templates have version suffixes (for example, base-settings-1.yaml, base-settings-2.yaml, etc.) to identify the sequence in which the versions are created in the book. In most cases, section headers in the book identify the version of the file being worked on in that section.

You can copy each chapter's files and folders, as needed, from the chapter's directory into your ~/aja2 directory if you wish the directory paths to appear as written in the book, or you can run the playbooks for each chapter from within the chapter's directory.

------------------------------------------------------------

*Day One: Automating Junos with Ansible, 2nd Edition* is available as a free PDF on [Juniper J-Net](https://www.juniper.net/us/en/training/jnbooks/day-one/automation-series/automating-junos-ansible/); for eBooks get it on [Apple iBooks/iTunes](https://itunes.apple.com/us/book/day-one-automating-junos-with-ansible/id1351397873?mt=11) or on [Amazon for Kindle](https://www.amazon.com/Day-One-Automating-Junos®-Ansible-ebook/dp/B079YZDVYJ). For print books purchase at the [Day One Print Store](http://store.vervante.com/c/v/V4081804173.html).
