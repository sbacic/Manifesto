###Manifesto
Manifesto generates your HTML5 manifests for you.

####Features
+ recursive searching
+ crawls directories, local and remote files
+ filters
+ custom manifest templates

####Installation
Manifesto requires `PyYaml` to work. To use Manifesto, simply download the package and type `manifesto` in your terminal. You may want to add it to ```~/bin/``` for ease of use. 

####Usage
Manifesto compiles a cache.manifest file based on the instructions provided in a yaml file. For more information, check the provided .yaml file. This tool should be used as a helper - don't expect it to provide you with fully functioning manifest files in all circumstances. A couple of things you should be aware of - always run manifesto in the same dir as the one your (future) manifest will be in to avoid problems with relative paths. Right now, only CSS and HTML crawling is supported (though you're free to add your own crawling rules). Lastly, certain CDNs deliver different CSS with different fonts depending on the user agent. 

####License
This software is distributed under the MIT license.
