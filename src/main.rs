use std::fs;
use std::path;
use std::env;

use yaml_rust::{YamlLoader, Yaml};//, yaml};

//https://github.com/chyh1990/yaml-rust/blob/master/examples/dump_yaml.rs

mod kg;

fn main() {

/*
    let args: Vec<_> = env::args().collect();

    let fact_name = if args.len() <= 1 {"string"} else {args[1].as_str()};
	println!("Fact name is '{}'", fact_name);

    let search_path = if args.len() <= 2 {None} else {Some(args[2].as_str())};
	let file_path = find_fact_file(fact_name, search_path);

    if file_path.is_none() {
        println!("Can't find file for '{}'", fact_name);
        return;
    }

    let file_path = file_path.unwrap();

    let docs = read_fact_file(&file_path).unwrap();

    let data = &docs[0];

    process_fact(fact_name, data);
*/
}

#[allow(dead_code)]
fn find_fact_file(fact_name: &str, path_option: Option<&str>) -> Option<path::PathBuf>
{
    let search_path =
    match path_option {
        None => {
            let current_path = env::current_dir()
            .expect("Can't get current directory");

            current_path.to_str().unwrap().to_owned() + "/db"
        }
        Some(path_str) => {
            path_str.to_string()
        }
    };
    println!("Search in '{}'", search_path);

    for entry in fs::read_dir(search_path).ok()? {
        let entry = entry.ok()?;
        let path = entry.path();

        let metadata = fs::metadata(&path).ok()?;
        //println!("{:?}", path);
        if metadata.is_file() {
            let file_name = path.file_name().ok_or("No filename").ok()?;
            //println!("{:?}", file_name);
            let file_name = file_name.to_str()?;
            let file_name_n = &file_name[..fact_name.len()];
            //println!("{:?}", file_name_n);
            if file_name_n == fact_name {
                println!("Found file for '{}' as {:?}", fact_name, path);
                return Some(path);
            }
        }
    }

    None
}

#[allow(dead_code)]
fn read_fact_file(file_path: &path::PathBuf) -> Result<Vec<Yaml>, Box<dyn std::error::Error>>
{
    assert!(fs::exists(file_path).expect("Can't find file"));

    let file_contents: String =
        fs::read_to_string(file_path)
        .expect("Can't read file");

    let docs = YamlLoader::load_from_str(&file_contents)?;

    Ok(docs)
}

#[allow(dead_code)]
fn process_fact(fact_name: &str, data: &Yaml)
{
    println!("{:?}", data);
    println!("{:?}", data[fact_name]);
    //let fact_map: &yaml::Hash = data.into();
    //for (k, v) in *data {
    //    println!("{:?} -> {:?}", k, v);
    //}
}