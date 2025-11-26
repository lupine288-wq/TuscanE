#!/bin/bash

if [[ $1 == "" ]]; then
    echo "arg1 - the path to the project, where high-level pom.xml is"
    echo "arg2 - the path to the mainAgent"
    # echo "arg2 - (Optional) Custom version for the artifact (e.g., 1.1.0, 1.2.0-SNAPSHOT). Default is $ARTIFACT_VERSION"
    exit
fi

if [[ ! $2 == "" ]]; then
    AGENT_JAR=$2
fi

crnt=`pwd`
working_dir=`dirname $0`
project_path=$1

cd ${project_path}
project_path=`pwd`
cd - > /dev/null

cd ${working_dir}

OPTION="-javaagent:${AGENT_JAR} -Xbootclasspath/a:${AGENT_JAR}"

javac PomFile.java
find ${project_path} -name pom.xml | grep -v "src/" | java PomFile ${OPTION}
rm -f PomFile.class

cd ${crnt}
