import React, { useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import Lottie from 'react-lottie';
import animationData from './myanimation.json';  // Path to your Lottie file

function App() {
  const [open, setOpen] = useState(false);

  // Toggle dialog visibility
  const handleClickOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  // Lottie options
  const defaultOptions = {
    loop: true,
    autoplay: true, // Animation will start immediately
    animationData: animationData, // Path to your Lottie file
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice',
    },
  };

  return (
    <div>
      {/* Button to open dialog */}
      <Button variant="contained" color="primary" onClick={handleClickOpen}>
        Open Lottie Animation
      </Button>

      {/* Dialog with Lottie animation */}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Lottie Animation</DialogTitle>
        <DialogContent>
          <Lottie options={defaultOptions} height={400} width={400} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App;
