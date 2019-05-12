export PYTHON_DIR='/usr/local/lib/python2.7/dist-packages'
export CURRENT_DIR=`pwd`

export CODE_DIR="ed_helper_publisher"
pip uninstall $CODE_DIR -y
rm -rf $PYTHON_DIR/${CODE_DIR}
tar xvfz $CURRENT_DIR/dist/${CODE_DIR}.tar.gz -C $PYTHON_DIR/
