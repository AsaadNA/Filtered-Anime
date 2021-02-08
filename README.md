# Filtered-Anime

Tool to bulk download anime episodes from https://gogoanime.sh


## Features

- Download **bulk** episodes or **single**
- Control the quality of the download [**360p**,**480p**,**720p**]
- Automatic quality selector if the desired quality is not available
- Retrieve info of animes such as [**Type** , **Total episode count** , **Release date** , **Genres** , **Completion status**]
- Anime suggestions using the anime name



## Usage

- **L** = low quality (360p)
- **M** = Medium quality (480p)
- **H** = High quality (720p)
- **[NOTE]** When wanting add a space b/w name kindly use a **-** for example **psycho-pass**
- **[NOTE]** Search the anime using the **SEO** name . If you do not know the seo name .. kindly see the end of readme

## Bulk downloading

```bash
python filteredanime.py [animeName] [episodeStart] [episodeEnd] [l,m,h]
python filteredanime.py gintama 245 250 h
```

![filteredanime #bulk](https://user-images.githubusercontent.com/70785015/107155881-cb351380-699c-11eb-8793-f43f7b354e21.PNG)

## Single download

```bash
python filteredanime.py [animeName] [episode] [l,m,h]
python filteredanime.py gintama 245 h
```

![filteredanime #single](https://user-images.githubusercontent.com/70785015/107155879-ca03e680-699c-11eb-8582-05017cbc8381.PNG)

## For Finding anime info

```bash
python filteredanime.py [animeName] info
python filteredanime.py gintama info
```

![filteredanime #info](https://user-images.githubusercontent.com/70785015/107155876-c8d2b980-699c-11eb-8bf2-ec2714db6404.PNG)


## If you need to find SEO name

Type any related name to the original anime , the tool will automatically give you the suggested names with the corresponding **SEO** names [in pink color]

![filteredanime #suggestions](https://user-images.githubusercontent.com/70785015/107155880-ca9c7d00-699c-11eb-80fa-ece295f66967.PNG)

