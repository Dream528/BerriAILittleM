
"use client";

import React, { useState, useEffect, useRef } from "react";
import { Button, TextInput, Grid, Col } from "@tremor/react";
import { Card, Metric, Text } from "@tremor/react";
import { Button as Button2, Modal, Form, Input, InputNumber, Select, message } from "antd";
import { keyCreateCall } from "./networking";

const { Option } = Select;

interface CreateKeyProps {
  userID: string;
  accessToken: string;
  proxyBaseUrl: string;
  data: any[] | null;
  setData: React.Dispatch<React.SetStateAction<any[] | null>>;
}

const CreateKey: React.FC<CreateKeyProps> = ({
  userID,
  accessToken,
  proxyBaseUrl,
  data,
  setData,
}) => {
  const [form] = Form.useForm();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [apiKey, setApiKey] = useState(null);

  const handleOk = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setApiKey(null);
  };

  const handleCreate = async (values) => {
    try {
      message.info("Making API Call");
      setIsModalVisible(true);
      const response = await keyCreateCall(proxyBaseUrl, accessToken, userID, values);
      setData([...data, response]);
      setApiKey(response["key"]);
      message.success("API Key Created");
    } catch (error) {
      console.error("Error creating the key:", error);
    }
  };

  return (
    <div>
      <Button className="mx-auto" onClick={() => setIsModalVisible(true)}>
        + Create New Key
      </Button>
      <Modal
        title="Create Key"
        visible={isModalVisible}
        width={800}
        footer={null}
      >
        <Form form={form} onFinish={handleCreate} labelCol={{ span: 6 }} wrapperCol={{ span: 16 }} labelAlign="left">
        
          <Form.Item
            label="Key Name"
            name="key_alias"
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Models"
            name="models"
          >
            <Input placeholder="Enter models separated by commas" />
          </Form.Item>
          

          <Form.Item
            label="Max Budget (USD)"
            name="max_budget"
          >
            <InputNumber step={0.01} precision={2} width={200}/>
          </Form.Item>
          <Form.Item
            label="Duration"
            name="duration"
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="Metadata"
            name="metadata"
          >
            <Input.TextArea rows={4} placeholder="Enter metadata as JSON" />
          </Form.Item>
          
        </Form>
        <div style={{ textAlign: 'right', marginTop: '10px' }}>
    <Button type="primary" htmlType="submit" onClick={handleCreate}>
      Create Key
    </Button>
  </div>
      </Modal>
      {apiKey && (
        <Modal
          title="Save your key"
          visible={isModalVisible}
          onOk={handleOk}
          onCancel={handleCancel}
        >
          {/* Display the result here */}
          <p>
            API Key: {apiKey} <br />
            {/* Display other API response details here */}
          </p>
        </Modal>
      )}
    </div>
  );
};

export default CreateKey;
