Project History: lizhifm 
-----------------------

#### 0.0.6 (2015-02-08) 
----------------------------------------
#### Behavioural Changes
* + hot_anchor & good_anchor
* depends on `prettytable`

#### Bugfixes
* null


#### 0.0.5 (2015-02-02) 
----------------------------------------
#### Behavioural Changes
* set default dir '$HOME/Music/LizhiFM'

#### Bugfixes
* os.makedirs


#### 0.0.4 (2015-01-28) 
----------------------------------------
#### Behavioural Changes
* replace `download` with `downloadhelper`

#### Bugfixes
* null


#### 0.0.3 (2015-01-28) 
----------------------------------------

#### Behavioural Changes
* null

#### Bugfixes
* requests_obj.content need decode requests_obj.encoding
  ```python3
    req.content.decode(req.encoding)
    (Tips: Because Python3 auto unicode, so we need decode the raw material to unicode, Right ?)
  ```
* 

  
#### 0.0.2 (2015-01-28) 
----------------------------------------

#### Behavioural Changes
* add functions: download, search
* use eval func

#### Bugfixes
* fix support python3

