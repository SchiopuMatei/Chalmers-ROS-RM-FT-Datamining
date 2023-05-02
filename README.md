# Chalmers-ROS-RM-FT-Datamining
ROS datamining project for Chalmers University of Technology


- Install Python 3.7 (see [here](https://wiki.python.org/moin/BeginnersGuide/Download))
- [optional] setup a Python virtual environment in order to keep all the modules always available and do not run into conflicts with other Python projects (see [here](https://virtualenv.pypa.io/en/latest/))
- Install the following Python modules:
  - git
  - bs4
  - ast
  - urllib3
  - certifi
  - pickle
- configure and run *rosmap* ([instructions](https://github.com/jr-robotics/rosmap)) and collect its results into the following files:
  - `dataset/repos_mining_data/intermediateResults0_rosmap_github.json`
  - `dataset/repos_mining_data/intermediateResults0_all_bitbucket.json`
  - `dataset/repos_mining_data/intermediateResults0_all_gitlab.json`

- run [merge_counter.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/merge_counter.py)
- run [explorer.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/explorer.py)
- run [cloner.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/cloner.py)
- run [detector.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/detector.py)
- run [metrics_manager.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/metrics_manager.py)



Based on

@article{JSS_ROS_2021,
  title = {{Mining guidelines for architecting robotics software}},
  journal = {Journal of Systems and Software},
  volume = {178},
  pages = {110969},
  year = {2021},
  issn = {0164-1212},
  doi = {https://doi.org/10.1016/j.jss.2021.110969},
  url = {https://www.sciencedirect.com/science/article/pii/S0164121221000662},
  author = {Ivano Malavolta and Grace A. Lewis and Bradley Schmerl and Patricia Lago and David Garlan}
}
