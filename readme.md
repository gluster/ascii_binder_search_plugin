# AsciiBinder Search Plugin

## What is this?
This is a small plugin that generates a data.json which contains the content and title and put it in each distro. This file is indexed with search template later. This plugin by default provides a search template that is ready to use but if you want you can plug your own search template. See the instructions below.

## Install instructions
- Run ``` pip install git+github.com/smitthakkar96/ascii_binder_search_plugin ``` to install it

## Usage
- To generate documentation you must run ``` ascii_binder_search ``` and it will do it's magic. I know many of you floks might wanna have your own search page design and to achieve that download [search.html](https://raw.githubusercontent.com/smitthakkar96/ascii_binder_search_plugin/master/static/search.html) and modfiy it accordingly. Now it's time to add it to the docs to do so run ``` ascii_binder_search -s <filename> ```
