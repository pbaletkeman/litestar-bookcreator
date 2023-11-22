book
* ### meta data section:
  * meta data section is a collection of meta data lines
  * meta data line is one meta tag with zero or more meta data attributes
  * meta data tag has a tag name and zero or one value
  * meta data attribute has a name and a value

* ### manifest section:
  * manifest has one or more item tags
  * item tags have: 
    * one HREF attribute
    * one ID attribute
    * one MEDIATYPE attribute
    * one PROPERTIES attribute

* ### spine section
  * one SPINE TAG:
    * TOC attribute
      * NCX version attribute value
  * one or more ITEMREF tags:
    * IDREF attribute
      *  value from manifest ID attribute

litestar --app main:app run --debug
