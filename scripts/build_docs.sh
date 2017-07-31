# clone the documentation repo
git clone https://github.com/smitthakkar96/fedora_docs_proposal

cd fedora_docs_proposal

# package docs
asciibinder package

# run search plugin on it
ascii_binder_search

# add no jekyll to the root dir of package folder
cd _package/main
touch .nojekyll
echo "Turn off jekyll" >> .nojekyll
