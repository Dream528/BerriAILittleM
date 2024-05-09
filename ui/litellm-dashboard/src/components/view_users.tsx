import React, { useState, useEffect } from "react";
import {
  Card,
  Title,
  Subtitle,
  Table,
  TableHead,
  TableHeaderCell,
  TableRow,
  TableCell,
  TableBody,
  Tab,
  Text,
  TabGroup,
  TabList,
  TabPanels,
  Metric,
  Grid,
  TabPanel,
  Select,
  SelectItem,
  Dialog, 
  DialogPanel,
  Icon,
  TextInput,
} from "@tremor/react";
import { userInfoCall, adminTopEndUsersCall } from "./networking";
import { Badge, BadgeDelta, Button } from "@tremor/react";
import RequestAccess from "./request_model_access";
import CreateUser from "./create_user_button";
import Paragraph from "antd/es/skeleton/Paragraph";
import InformationCircleIcon from "@heroicons/react/outline/InformationCircleIcon";

interface ViewUserDashboardProps {
  accessToken: string | null;
  token: string | null;
  keys: any[] | null;
  userRole: string | null;
  userID: string | null;
  teams: any[] | null;
  setKeys: React.Dispatch<React.SetStateAction<Object[] | null>>;
}

const ViewUserDashboard: React.FC<ViewUserDashboardProps> = ({
  accessToken,
  token,
  keys,
  userRole,
  userID,
  teams,
  setKeys,
}) => {
  const [userData, setUserData] = useState<null | any[]>(null);
  const [endUsers, setEndUsers] = useState<null | any[]>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [openDialogId, setOpenDialogId] = React.useState<null | number>(null);
  const [selectedItem, setSelectedItem] = useState<null | any>(null);
  const defaultPageSize = 25;

  useEffect(() => {
    if (!accessToken || !token || !userRole || !userID) {
      return;
    }
    const fetchData = async () => {
      try {
        // Replace with your actual API call for model data
        const userDataResponse = await userInfoCall(
          accessToken,
          null,
          userRole,
          true,
          currentPage,
          defaultPageSize
        );
        console.log("user data response:", userDataResponse);
        setUserData(userDataResponse);
      } catch (error) {
        console.error("There was an error fetching the model data", error);
      }
    };

    if (accessToken && token && userRole && userID) {
      fetchData();
    }


  }, [accessToken, token, userRole, userID, currentPage]);

  if (!userData) {
    return <div>Loading...</div>;
  }

  if (!accessToken || !token || !userRole || !userID) {
    return <div>Loading...</div>;
  }

  const onKeyClick = async (keyToken: String) => {
    try {
      const topEndUsers = await adminTopEndUsersCall(accessToken, keyToken);
      console.log("user data response:", topEndUsers);
      setEndUsers(topEndUsers);
    } catch (error) {
      console.error("There was an error fetching the model data", error);
    }
  };

  function renderPagination() {
    if (!userData) return null;

    const totalPages = Math.ceil(userData.length / defaultPageSize);

    return (
      <div className="flex justify-between items-center">
        <div>
          Showing Page {currentPage+1} of {totalPages}
        </div>
        <div className="flex">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-l focus:outline-none"
            disabled={currentPage === 0}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            &larr; Prev
          </button>
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r focus:outline-none"
            // disabled={currentPage === totalPages}
            onClick={() => {
              setCurrentPage(currentPage + 1);
            }}
          >
            Next &rarr;
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ width: "100%" }}>
      <Grid className="gap-2 p-2 h-[80vh] w-full mt-8">
        <CreateUser userID={userID} accessToken={accessToken} teams={teams}/>
        <Card className="w-full mx-auto flex-auto overflow-y-auto max-h-[80vh] mb-4">
        <div className="mb-4 mt-1">
        <Text>These are Users on LiteLLM that created API Keys. Automatically tracked by LiteLLM</Text>
       
        </div>
          <TabGroup>

            <TabPanels>
              <TabPanel>
                
                <Table className="mt-5">
                  <TableHead>
                    <TableRow>
                      <TableHeaderCell>User ID</TableHeaderCell>
                      <TableHeaderCell>User Email</TableHeaderCell>
                      <TableHeaderCell>User Models</TableHeaderCell>
                      <TableHeaderCell>User Spend ($ USD)</TableHeaderCell>
                      <TableHeaderCell>User Max Budget ($ USD)</TableHeaderCell>
                      <TableHeaderCell>User API Key Aliases</TableHeaderCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {userData.map((user: any) => (
                      <TableRow key={user.user_id}>
                        <TableCell>{user.user_id}</TableCell>
                        <TableCell>{user.user_email}</TableCell>
                        
                        <TableCell>
                          {user.models && user.models.length > 0
                            ? user.models
                            : "All Models"}
                        </TableCell>
                        <TableCell>{user.spend ? user.spend?.toFixed(2) : 0}</TableCell>
                        <TableCell>
                          {user.max_budget ? user.max_budget : "Unlimited"}
                        </TableCell>
                        <TableCell>
                          <Grid numItems={2}>
                          {user && user.key_aliases
                              ? user.key_aliases.filter((key: any) => key !== null).length > 0
                                ? <Badge size={"xs"} color={"indigo"}>{user.key_aliases.filter((key: any) => key !== null).join(', ') }</Badge>
                                : <Badge size={"xs"} color={"gray"}>No Keys</Badge>
                              : <Badge size={"xs"} color={"gray"}>No Keys</Badge>}
                          {/* <Text>{user.key_aliases.filter(key => key !== null).length} Keys</Text> */}
                        {/* <Icon icon={InformationCircleIcon} onClick= {() => {
                          setOpenDialogId(user.user_id)
                          setSelectedItem(user)
                        }}>View Keys</Icon> */}

                          </Grid>

                        </TableCell>

                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabPanel>
              <TabPanel>
                <div className="flex items-center">
                  <div className="flex-1"></div>
                  <div className="flex-1 flex justify-between items-center">
   
                  </div>
                </div>
                {/* <Table className="max-h-[70vh] min-h-[500px]">
                  <TableHead>
                    <TableRow>
                      <TableHeaderCell>End User</TableHeaderCell>
                      <TableHeaderCell>Spend</TableHeaderCell>
                      <TableHeaderCell>Total Events</TableHeaderCell>
                    </TableRow>
                  </TableHead>

                  <TableBody>
                    {endUsers?.map((user: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{user.end_user}</TableCell>
                        <TableCell>{user.total_spend}</TableCell>
                        <TableCell>{user.total_events}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table> */}
              </TabPanel>
            </TabPanels>
          </TabGroup>
        </Card>
        {renderPagination()}
      </Grid>
      {/* <Dialog
  open={openDialogId !== null}
  onClose={() => {
    setOpenDialogId(null);
  }}

>
  <DialogPanel>
  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <Title>Key Aliases</Title>

    <Text>
    {selectedItem && selectedItem.key_aliases
 ? selectedItem.key_aliases.filter(key => key !== null).length > 0
   ? selectedItem.key_aliases.filter(key => key !== null).join(', ')
   : 'No Keys'
 : "No Keys"}
    </Text>
    </div>
  </DialogPanel>
</Dialog> */}
    </div>

  );
};

export default ViewUserDashboard;
