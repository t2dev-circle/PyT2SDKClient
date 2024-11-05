#ifndef T2APIH
#define T2APIH

#include "t2sdk_interface.h"
#include <windows.h>
#include <string>
#include <vector>
#include <map>
#include <iostream>
using namespace std;

class UtilsHelper
{
public:
    static string gbk2utf8(const char *data);
	static string utf82gbk(const char *data);
	static string gbk2utf8Str(const string &gbk);
	static string utf82gbkStr(const string &utf8);
};

class T2Api
{
public:
    T2Api();
    ~T2Api();
public:
    bool init();
    void release();

    bool connect();
    bool send(const map<string, string> &req);
    bool recv();
public:
    void setUtf8(bool flag);
    
    const vector<map<string, string>> & getRecords() const;
    const string & getErrMsg();
private:
    bool packRequest(const map<string, string> &req);
    bool packResponse(vector<map<string, string>> &rsp);

    void clearResponse();

    bool getInt(int index, string &value);
    bool getDouble(int index, string &value);
    bool getChar(int index, string &value);
    bool getString(int index, string &value);
    bool getRaw(int index, string &value);
private:
    CConfigInterface *m_config;
    CConnectionInterface *m_conn;
    IBizMessage *m_sendMsg;
    IBizMessage *m_recvMsg;
    IF2Packer *m_packer;
    IF2UnPacker *m_unpacker;

    bool m_utf8;
    int m_sendHandle;
    string m_errMsg;

    vector<map<string, string>> m_records;
};

#endif