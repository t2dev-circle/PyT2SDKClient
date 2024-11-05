
#include "t2api.h"

string UtilsHelper::gbk2utf8(const char *data)
{
    if (data == nullptr)
    {
        return "";
    }

    return UtilsHelper::gbk2utf8Str(string(data, strlen(data)));
}

string UtilsHelper::utf82gbk(const char *data)
{
    if (data == nullptr)
    {
        return "";
    }

    return UtilsHelper::utf82gbkStr(string(data, strlen(data)));
}

string UtilsHelper::gbk2utf8Str(const string &gbk)
{
    string outUtf8 = "";
    
    int n = MultiByteToWideChar(CP_ACP, 0, gbk.c_str(), -1, nullptr, 0);
    
    WCHAR *str1 = new WCHAR[n];
    MultiByteToWideChar(CP_ACP, 0, gbk.c_str(), -1,str1, n);
    n = WideCharToMultiByte(CP_UTF8, 0, str1, -1, nullptr, 0, nullptr, nullptr);
    
    char *str2 = new char[n];
    WideCharToMultiByte(CP_UTF8, 0, str1, -1, str2, n, nullptr, nullptr);
    
    outUtf8 = str2;

    delete[]str1;
    str1 = nullptr;

    delete[]str2;
    str2 = nullptr;

    return outUtf8;
}

string UtilsHelper::utf82gbkStr(const string &utf8)
{
    string outGBK = "";

    int n = MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, nullptr, 0);
   
    WCHAR *str1 = new WCHAR[n];
    MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, str1, n);
    n = WideCharToMultiByte(CP_ACP, 0, str1, -1, nullptr, 0, nullptr, nullptr);
    
    char *str2 = new char[n];
    WideCharToMultiByte(CP_ACP, 0, str1, -1, str2, n, nullptr, nullptr);
    
    outGBK = str2;
    
    delete[] str1;
    str1 = nullptr;
    
    delete[] str2;
    str2 = nullptr;
    
    return outGBK;
}

T2Api::T2Api()
{
    m_config = nullptr;
    m_conn = nullptr;
    m_sendMsg = nullptr;
    m_recvMsg = nullptr;
    m_packer = nullptr;
    m_unpacker = nullptr;

    m_utf8 = true;
    m_sendHandle = 0;
    m_errMsg = "";
}

T2Api::~T2Api()
{
    release();
}

bool T2Api::init()
{
    m_config = NewConfig();
    if (m_config == nullptr)
    {
        return false;
    }

    m_config->AddRef();
    m_config->SetString("t2sdk", "servers", "121.41.126.194:9359");
    m_config->SetString("t2sdk", "license_file", "license.dat");
    m_config->SetString("t2sdk", "license_file", "license.dat");
    m_config->SetString("t2sdk", "if_sendRecv_log", "1");
    m_config->SetString("t2sdk", "if_error_log", "1");
    m_config->SetString("t2sdk", "writedata", "1");

    return true;
}

void T2Api::release()
{
    if (m_unpacker != nullptr)
    {
        m_unpacker->Release();
        m_unpacker = nullptr;
    }

    if (m_packer != nullptr)
    {
        m_packer->Release();
        m_packer = nullptr;
    }

    if (m_recvMsg != nullptr)
    {
        m_recvMsg->Release();
        m_recvMsg = nullptr;
    }

    if (m_sendMsg != nullptr)
    {
        m_sendMsg->Release();
        m_sendMsg = nullptr;
    }

    if (m_conn != nullptr)
    {
        m_conn->Release();
        m_conn = nullptr;
    }

    if (m_config != nullptr)
    {
        m_config->Release();
        m_config = nullptr;
    }
}

void T2Api::setUtf8(bool flag)
{
    m_utf8 = flag;
}

bool T2Api::connect()
{
    m_errMsg = "";
    
    if (m_config == nullptr)
    {
        return false;
    }

    if (m_conn != nullptr)
    {
        m_conn->Release();
        m_conn = nullptr;
    }

    m_conn = NewConnection(m_config);
    if (m_conn == nullptr)
    {
        return false;
    }

    m_conn->AddRef();

    int ret = m_conn->Create2BizMsg(nullptr);
    if (ret != 0)
    {
        return false;
    }

    // 超时单位毫秒
    ret = m_conn->Connect(1000 * 5);
    if (ret != 0)
    {
        m_errMsg = m_conn->GetErrorMsg(ret);

        return false;
    }

    return true;
}

bool T2Api::send(const map<string, string> &req)
{
    m_errMsg = "";

    if (m_sendMsg != nullptr)
    {
        m_sendMsg->Release();
        m_sendMsg = nullptr;
    }

    m_sendMsg = NewBizMessage();
    if (m_sendMsg == nullptr)
    {
        return false;
    }

    m_sendMsg->AddRef();

    map<string, string> &tmp = const_cast<map<string, string> &>(req);

    string funcNo = tmp["func_no"];
    m_sendMsg->SetFunction(atoi(funcNo.c_str()));
	m_sendMsg->SetPacketType(REQUEST_PACKET);
    m_sendMsg->SetSystemNo(2); // 2-普通 3-信用 5-个股期权

    packRequest(req);

    m_sendMsg->SetContent(m_packer->GetPackBuf(), m_packer->GetPackLen());
    int ret = m_conn->SendBizMsg(m_sendMsg, 0);
    if (ret < 0)
    {
        m_errMsg = m_conn->GetErrorMsg(ret);

        return false;
    }

    m_sendHandle = ret;

    return true;
}

bool T2Api::recv()
{
    if (m_conn == nullptr)
    {
        return false;
    }

    int ret = m_conn->RecvBizMsg(m_sendHandle, &m_recvMsg, 1000 * 5);
    if (ret != 0)
    {
        m_errMsg = m_conn->GetErrorMsg(ret);

        return false;
    }

    if (m_recvMsg == nullptr)
    {
        return false;
    }

    int errNo = m_recvMsg->GetErrorNo();
    if (errNo != 0)
    {
        m_errMsg = m_recvMsg->GetErrorInfo();
        
        return false;
    }

    return packResponse(m_records);
}

const vector<map<string, string>> & T2Api::getRecords() const
{
    return m_records;
}

const string & T2Api::getErrMsg()
{
    if (m_utf8)
    {
        m_errMsg = UtilsHelper::gbk2utf8Str(m_errMsg);
    }

    return m_errMsg;
}

bool T2Api::packRequest(const map<string, string> &req)
{
    if (req.size() == 0)
    {
        return false;
    }

    if (m_packer != nullptr)
    {
        m_packer->FreeMem(m_packer->GetPackBuf());
        m_packer->Release();
        m_packer = nullptr;
    }

    m_packer = NewPacker(2);
    m_packer->AddRef();
    m_packer->BeginPack();

    for (auto iter = req.begin(); iter != req.end(); ++iter)
    {
        m_packer->AddField(iter->first.c_str(), 'S', iter->second.length());
    }

    for (auto iter = req.begin(); iter != req.end(); ++iter)
    {
        m_packer->AddStr(iter->second.c_str());
    }

    m_packer->EndPack();
    
    return true;
}

bool T2Api::packResponse(vector<map<string, string>> &rsp)
{
    clearResponse();

    if (m_recvMsg == nullptr)
    {
        return false;
    }

    int len = 0;
    const void *buff = m_recvMsg->GetContent(len);

    if (m_unpacker != nullptr)
    {
        m_unpacker->Release();
        m_unpacker = nullptr;
    }

    m_unpacker = NewUnPacker((void *)buff, len);
    if (m_unpacker == nullptr)
    {
        return false;
    }

    m_unpacker->AddRef();

    m_unpacker->SetCurrentDatasetByIndex(0);
    m_unpacker->First();

    int errNo = m_unpacker->GetInt("error_no");
    if (errNo != 0)
    {
        m_errMsg = m_unpacker->GetStr("error_info");
        cout << errNo << "|" << m_errMsg << endl;

        return false;
    }

    m_unpacker->SetCurrentDatasetByIndex(1);

    int rowCount = m_unpacker->GetRowCount();
    int colCount = m_unpacker->GetColCount();

    cout << "pack:" << len << "|" << rowCount << "|" << colCount << endl;

    map<string, string> record;

    for (auto i = 0; i < rowCount; i++)
    {
        for (auto j = 0; j < colCount; j++)
        {
            string colName = m_unpacker->GetColName(j);
            char colType = m_unpacker->GetColType(j);
            string colValue = "";

            switch (colType)
            {
            case 'I':
                getInt(j, colValue);
                break;
            case 'F':
                getDouble(j, colValue);
                break;
            case 'C':
                getChar(j, colValue);
                break;
            case 'S':
                getString(j, colValue);
                break;
            case 'R':
                getRaw(j, colValue);
                break;
            default:
                break;
            }

            cout << i << "|" << j << "|" << colName << "|" << colType << "|" << colValue << endl;

            if (m_utf8)
            {
                colValue = UtilsHelper::gbk2utf8Str(colValue);
            }

            record.insert(make_pair(colName, colValue));
        }

        rsp.push_back(record);

        m_unpacker->Next();
    }

    return true;
}

void T2Api::clearResponse()
{
    vector<map<string, string>> tmp;

    m_records.swap(tmp);
}

bool T2Api::getInt(int index, string &value)
{
    value = "";

    if (m_unpacker == nullptr)
    {
        return false;
    }

    value = std::to_string(m_unpacker->GetIntByIndex(index));
    
    return true;
}

bool T2Api::getDouble(int index, string &value)
{
    value = "";

    if (m_unpacker == nullptr)
    {
        return false;
    }

    value = std::to_string(m_unpacker->GetDoubleByIndex(index));

    return true;
}

bool T2Api::getChar(int index, string &value)
{
    value = "";

    if (m_unpacker == nullptr)
    {
        return false;
    }

    char data = m_unpacker->GetCharByIndex(index);

    value = string(1, data);
    
    return true;
}

bool T2Api::getString(int index, string &value)
{
    value = "";

    if (m_unpacker == nullptr)
    {
        return false;
    }

    const char *data = m_unpacker->GetStrByIndex(index);
    if (data == nullptr)
    {
        return false;
    }

    value = data;

    return true;
}

bool T2Api::getRaw(int index, string &value)
{
    value = "";

    if (m_unpacker == nullptr)
    {
        return false;
    }

    int len = 0;
    void *data = m_unpacker->GetRawByIndex(index, &len);

    if (data == nullptr || len <= 0)
    {
        return false;
    }

    value = string((const char *)data, len);

    return true;
}
